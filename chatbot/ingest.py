"""
Ingestion + chunking cho chatbot StudentHub UET.

Đặt file này cạnh thư mục data/ (chatbot/ingest.py), rồi chạy:
    python ingest.py --chunk-only   # chỉ cắt chunk -> chunks.jsonl (không cần chromadb/model)
    python ingest.py                # cắt chunk + embedding + nạp vào Qdrant

Chạy lại bao nhiêu lần cũng được: mỗi lần chạy xoá collection cũ và nạp lại từ đầu.
"""
import argparse
import json
import re
import statistics
from pathlib import Path

import yaml
from pydantic import ValidationError

from schemas import Chunk, ChunkMeta, DocumentMeta

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
CHUNKS_FILE = BASE / "chunks.jsonl"
QDRANT_DIR = BASE / "qdrant_data"
COLLECTION = "studenthub_docs"
EMBED_MODEL = "BAAI/bge-m3"

CHILD_MAX = 900       # chunk con: dài hơn mức này thì cắt tiếp (con nhỏ -> tìm kiếm chính xác)
MIN_CHARS = 150       # section ngắn hơn mức này thì gộp với section bên cạnh
OVERLAP_MAX = 0       # không lặp đoạn giữa các chunk con: ngữ cảnh đã có chunk cha lo

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


# ---------- 1. Đọc file + front matter ----------
def load_doc(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path.name}: thiếu front matter")
    try:
        meta = DocumentMeta.model_validate(yaml.safe_load(m.group(1)) or {})
    except ValidationError as e:
        raise SystemExit(f"{path.name}: front matter không hợp lệ\n{e}")
    return meta, m.group(2)


# ---------- 2. Tách theo heading ----------
def split_sections(body: str, title: str):
    """Trả về list (heading_path, text). Heading cấp 1 (#) bỏ qua vì trùng title."""
    sections, stack, buf = [], {}, []

    def flush():
        text = "\n".join(buf).strip()
        # bỏ dòng '---' (kẻ ngang) thừa
        text = "\n".join(l for l in text.split("\n") if l.strip() != "---").strip()
        if text:
            path = [title] + [stack[k] for k in sorted(stack)]
            sections.append((" > ".join(path), text))
        buf.clear()

    for line in body.split("\n"):
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) >= 2:
            flush()
            level = len(m.group(1))
            stack = {k: v for k, v in stack.items() if k < level}
            stack[level] = m.group(2).strip("* ")
        elif m:  # heading cấp 1
            flush()
        else:
            buf.append(line)
    flush()
    return sections


# ---------- 3. Cắt section dài thành các đơn vị rồi gom lại ----------
def to_units(text: str):
    """Đơn vị = 1 khoản ('1. ...' kèm các ý a), b) bên dưới), 1 đoạn văn, hoặc 1 bảng."""
    lines, units, cur, i = text.split("\n"), [], [], 0

    def flush():
        if cur:
            units.append("\n".join(cur))
            cur.clear()

    while i < len(lines):
        l = lines[i]
        if l.lstrip().startswith("|"):  # bảng markdown
            flush()
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            units.extend(split_table(lines[i:j]))
            i = j
            continue
        if not l.strip():
            flush()
        else:
            if re.match(r"^\d+\.\s", l):
                flush()
            cur.append(l)
        i += 1
    flush()
    return units


def split_table(rows):
    """Bảng vừa thì giữ nguyên; quá dài thì cắt theo hàng, lặp lại header ở mỗi mảnh."""
    whole = "\n".join(rows)
    if len(whole) <= CHILD_MAX or len(rows) <= 3:
        return [whole]
    header, body = rows[:2], rows[2:]
    pieces, cur = [], []
    for r in body:
        if cur and len("\n".join(header + cur + [r])) > CHILD_MAX:
            pieces.append("\n".join(header + cur))
            cur = []
        cur.append(r)
    if cur:
        pieces.append("\n".join(header + cur))
    return pieces


def split_big_unit(unit: str):
    """Một khoản quá dài: cắt theo dòng; các mảnh sau lặp lại dòng tiêu đề của khoản."""
    lines = unit.split("\n")
    head, out, cur, base = lines[0], [], [], 0
    for l in lines:
        if len(cur) > base and len("\n".join(cur + [l])) > CHILD_MAX:
            out.append("\n".join(cur))
            cur, base = [head], 1
        cur.append(l)
    if cur:
        out.append("\n".join(cur))
    return out


def pack(text: str):
    if len(text) <= CHILD_MAX:
        return [text]
    units = []
    for u in to_units(text):
        units.extend(split_big_unit(u) if len(u) > CHILD_MAX else [u])
    chunks, cur = [], []
    for u in units:
        if cur and len("\n\n".join(cur + [u])) > CHILD_MAX:
            chunks.append("\n\n".join(cur))
            last = cur[-1]
            cur = [last] if len(cur) > 1 and len(last) <= OVERLAP_MAX and not last.startswith("|") else []
        cur.append(u)
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


# ---------- 4. Gộp chunk quá ngắn ----------
def merge_tiny(items):
    """items: list [path, text] của các section. Section quá ngắn -> gộp vào section kế
    (nếu là phần dẫn của nó) hoặc section liền trước."""
    out, i = [], 0
    while i < len(items):
        path, text = items[i]
        if len(text) < MIN_CHARS:
            nxt = items[i + 1] if i + 1 < len(items) else None
            if nxt and nxt[0].startswith(path):  # phần dẫn của section con
                items[i + 1] = [nxt[0], text + "\n\n" + nxt[1]]
                i += 1
                continue
            if out:
                out[-1][1] += "\n\n" + text
                i += 1
                continue
        out.append([path, text])
        i += 1
    return out


# ---------- 5. Dựng chunk cha - con cho toàn bộ tài liệu ----------
def make_chunk(chunk_id, level, parent_id, heading_path, text, meta, path, idx):
    return Chunk(
        chunk_id=chunk_id,
        # text = nội dung có gắn đường dẫn heading, dùng để embedding và đưa cho LLM
        text=f"[{heading_path}]\n{text}",
        metadata=ChunkMeta(
            **meta.model_dump(),
            source_file=path.name,
            heading_path=heading_path,
            chunk_index=idx,
            level=level,
            parent_id=parent_id,
        ),
    )


def build_chunks(data_dir: Path):
    """Cha = nguyên 1 section (Điều/mục). Con = các mảnh nhỏ của section đó.
    Section ngắn (không phải cắt) chỉ có 1 chunk con, không có cha."""
    all_chunks = []
    for path in sorted(data_dir.glob("*.md")):
        meta, body = load_doc(path)
        sections = merge_tiny(split_sections(body, meta.title))
        n_parent = n_child = 0
        for heading_path, text in sections:
            pieces = pack(text)
            parent_id = None
            if len(pieces) > 1:
                parent_id = f"{meta.doc_id}-p{n_parent:03d}"
                all_chunks.append(make_chunk(parent_id, "parent", None, heading_path, text, meta, path, n_parent))
                n_parent += 1
            for piece in pieces:
                all_chunks.append(
                    make_chunk(f"{meta.doc_id}-{n_child:03d}", "child", parent_id, heading_path, piece, meta, path, n_child)
                )
                n_child += 1
    return all_chunks


def write_jsonl(chunks):
    with CHUNKS_FILE.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json(exclude_none=True) + "\n")


def print_stats(chunks):
    parents = [c for c in chunks if c.metadata.level == "parent"]
    children = [c for c in chunks if c.metadata.level == "child"]
    print(f"Tổng: {len(children)} chunk con (đem đi tìm kiếm) + {len(parents)} chunk cha (ngữ cảnh đưa cho LLM)")
    by_doc = {}
    for c in children:
        by_doc.setdefault(c.metadata.doc_id, []).append(len(c.text))
    for d, ls in by_doc.items():
        n_p = sum(1 for p in parents if p.metadata.doc_id == d)
        print(f"  {d:<22} {len(ls):>3} con | {n_p:>2} cha | con: min {min(ls):>4} tb {int(statistics.mean(ls)):>4} max {max(ls):>4} ký tự")


# ---------- 6. Embedding + nạp Qdrant ----------
def ingest(chunks):
    import uuid

    from qdrant_client import QdrantClient, models
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBED_MODEL)
    model.max_seq_length = 1024
    parents = {c.chunk_id: c for c in chunks if c.metadata.level == "parent"}
    children = [c for c in chunks if c.metadata.level == "child"]  # chỉ chunk con được embedding
    texts = [c.text for c in children]
    vectors = model.encode(texts, batch_size=16, normalize_embeddings=True, show_progress_bar=True)

    # Chế độ local: lưu ra thư mục, không cần chạy server. Sau này lên server/cloud thì đổi thành
    # QdrantClient(url="...", api_key="...")
    client = QdrantClient(path=str(QDRANT_DIR))
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=models.VectorParams(size=vectors.shape[1], distance=models.Distance.COSINE),
    )
    points = []
    for c, v in zip(children, vectors):
        payload = c.to_payload()
        if c.metadata.parent_id:  # đính kèm nguyên section cha để lúc trả lời đưa cho LLM
            payload["parent_text"] = parents[c.metadata.parent_id].text
        points.append(
            models.PointStruct(
                # Qdrant chỉ nhận id là số nguyên hoặc UUID -> sinh UUID cố định từ chunk_id
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, c.chunk_id)),
                vector=v.tolist(),
                payload=payload,
            )
        )
    client.upsert(collection_name=COLLECTION, points=points)
    print(f"Đã nạp {client.count(COLLECTION).count} chunk vào '{COLLECTION}' ({QDRANT_DIR})")

    # kiểm tra nhanh: câu hỏi mẫu phải ra đúng tài liệu (score càng CAO càng giống)
    for q in ["Xin bảng điểm thì nhận ở đâu?", "Điều kiện để học cùng lúc hai chương trình là gì?"]:
        qv = model.encode([q], normalize_embeddings=True)[0].tolist()
        res = client.query_points(collection_name=COLLECTION, query=qv, limit=3, with_payload=True)
        print(f"\nThử: {q}")
        for p in res.points:
            pid = p.payload.get("parent_id", "-")
            print(f"  {p.score:.3f} | {p.payload['chunk_id']} (cha: {pid}) | {p.payload['heading_path'].split(' > ', 1)[-1]}")
    client.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk-only", action="store_true", help="chỉ cắt chunk, không embedding")
    ap.add_argument("--data", default=str(DATA_DIR))
    args = ap.parse_args()

    chunks = build_chunks(Path(args.data))
    write_jsonl(chunks)
    print_stats(chunks)
    if not args.chunk_only:
        ingest(chunks)