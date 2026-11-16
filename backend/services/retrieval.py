"""Lightweight lexical retrieval and source excerpts for offline demo use."""

from collections import Counter
from functools import lru_cache
import math
import re
import unicodedata

from ..config import DENSE_MIN_SCORE, LEXICAL_STRONG_SCORE, MIN_RETRIEVAL_SCORE, TOP_K
from . import rerank as reranker
from .embeddings import dense_rank
from ..repositories.documents import data_signature, load_passages
from ..models import Hit, Passage


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    return "".join("d" if c == "đ" else c for c in value if unicodedata.category(c) != "Mn")


STOP_WORDS = {normalize(word) for word in {
    "và", "là", "của", "cho", "có", "được", "với", "trong", "khi",
    "ở", "tại", "về", "theo", "nào", "bao", "nhiêu", "như", "thế", "để",
    "em", "mình", "tôi", "bạn", "anh", "chị", "sinh", "viên", "trường",
    "cần", "phải", "đã", "sẽ", "một", "các", "những", "nếu", "không",
}}

QUERY_EXPANSIONS = {
    "gpa": ("diem trung binh", "ket qua hoc tap"),
    "cpa": ("diem trung binh tich luy",),
    "drl": ("diem ren luyen",),
    "qr": ("thanh toan", "chuyen khoan"),
    "hoc bong": ("khuyen khich hoc tap", "kkht"),
}


def tokens(value: str) -> list[str]:
    value = normalize(value)
    return [w for w in re.findall(r"[a-z0-9]+", value) if len(w) > 1 and w not in STOP_WORDS]


def expanded_tokens(value: str) -> list[str]:
    normalized = normalize(value)
    result = tokens(value)
    for phrase, expansions in QUERY_EXPANSIONS.items():
        if phrase in normalized:
            for expansion in expansions:
                result.extend(tokens(expansion))
    return result


@lru_cache(maxsize=2)
def _index(signature: tuple[tuple[str, int, int], ...]) -> tuple[list[Passage], list[Counter[str]], Counter[str], float]:
    passages = load_passages()
    counts = [Counter(tokens(p.heading + " " + p.text)) for p in passages]
    document_frequency: Counter[str] = Counter()
    for count in counts:
        document_frequency.update(count.keys())
    avg_length = sum(sum(c.values()) for c in counts) / max(len(counts), 1)
    return passages, counts, document_frequency, avg_length


RRF_K = 60
CANDIDATES = 20
RERANK_POOL = 8


def _bm25(question: str, passages: list[Passage], counts, df, avg_length) -> list[tuple[int, float]]:
    """[(passage index, score)] best first, for passages that match at least one term."""
    query_tokens = expanded_tokens(question)
    terms = set(query_tokens)
    if not terms:
        return []
    query_heading_phrases = {
        size: {tuple(query_tokens[i:i + size]) for i in range(len(query_tokens) - size + 1)}
        for size in (2, 3)
    }
    n = len(passages)
    term_idf = {
        term: math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
        for term in terms
    }
    results: list[tuple[int, float]] = []
    for index, (passage, count) in enumerate(zip(passages, counts)):
        length = sum(count.values())
        score = 0.0
        for term in terms:
            frequency = count[term]
            if not frequency:
                continue
            score += term_idf[term] * frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * length / max(avg_length, 1)))
        heading_terms = set(tokens(passage.heading))
        score += sum(0.7 for term in terms & heading_terms)
        heading_tokens = tokens(passage.heading)
        for size, weight in ((2, 1.8), (3, 2.5)):
            passage_heading_phrases = {tuple(heading_tokens[i:i + size]) for i in range(len(heading_tokens) - size + 1)}
            score += weight * len(passage_heading_phrases & query_heading_phrases[size])
        if score > 0:
            results.append((index, score))
    results.sort(key=lambda item: item[1], reverse=True)
    return results


def _select(ranked: list[Hit], limit: int) -> list[Hit]:
    """Take the best hits while keeping any one document from crowding out the rest."""
    selected: list[Hit] = []
    per_source: Counter[str] = Counter()
    for hit in ranked:
        if per_source[hit.passage.source] >= 3:
            continue
        selected.append(hit)
        per_source[hit.passage.source] += 1
        if len(selected) >= limit:
            break
    return selected


def search(question: str, limit: int = TOP_K) -> list[Hit]:
    """Hybrid search: BM25 fused with dense embeddings (RRF); BM25 alone when dense is unavailable."""
    passages, counts, df, avg_length = _index(data_signature())
    lexical = _bm25(question, passages, counts, df, avg_length)
    dense = dense_rank(question, passages, CANDIDATES)

    if not dense:
        if not lexical or lexical[0][1] < MIN_RETRIEVAL_SCORE:
            return []
        return _select([Hit(passages[i], score) for i, score in lexical], limit)

    # Dense similarity separates on-topic from off-topic questions far better than BM25 does;
    # a very strong exact keyword match can still rescue a short query.
    if dense[0][1] < DENSE_MIN_SCORE and not (lexical and lexical[0][1] >= LEXICAL_STRONG_SCORE):
        return []
    fused: dict[int, float] = {}
    for ranking in (lexical[:CANDIDATES], dense):
        for rank, (index, _) in enumerate(ranking, 1):
            fused[index] = fused.get(index, 0.0) + 1 / (RRF_K + rank)
    order = sorted(fused, key=fused.get, reverse=True)
    ranked = [Hit(passages[i], fused[i]) for i in order]
    if reranker.enabled():
        ranked = reranker.rerank(question, ranked[:RERANK_POOL]) + ranked[RERANK_POOL:]
    return _select(ranked, limit)


def extract_answer(question: str, hits: list[Hit]) -> str:
    """Return cited source lines when Gemini is not configured or available."""
    query_terms = set(expanded_tokens(question))
    query_tokens = expanded_tokens(question)
    asks_for_quantity = bool(re.search(r"\b(bao nhieu|may|toi da|it nhat)\b", normalize(question)))
    phrases = {tuple(query_tokens[index:index + 2]) for index in range(len(query_tokens) - 1)}
    passages, _, df, _ = _index(data_signature())
    n = len(passages)
    term_idf = {
        term: math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
        for term in query_terms
    }
    ranked_lines: list[tuple[float, int, str]] = []
    seen: set[str] = set()
    for source_number, hit in enumerate(hits, 1):
        for line in hit.passage.text.splitlines():
            line = line.strip()
            if len(line) < 20 or line == "---" or line in seen:
                continue
            seen.add(line)
            line_tokens = tokens(line)
            overlap = query_terms & set(line_tokens)
            if overlap:
                line_phrases = {tuple(line_tokens[index:index + 2]) for index in range(len(line_tokens) - 1)}
                score = sum(term_idf[term] for term in overlap) / max(len(line_tokens), 1) ** 0.25
                score += 2.0 * len(phrases & line_phrases) + 0.2 / source_number
                if asks_for_quantity and re.search(r"\d", line):
                    score += 3.0
                ranked_lines.append((score, source_number, line))
    ranked_lines.sort(reverse=True)
    excerpts = []
    for _, number, line in ranked_lines[:5]:
        clean_line = re.sub(r"^[-*]\s+", "", line)
        excerpts.append(f"- {clean_line[:500]} [{number}]")
    if not excerpts:
        excerpts = [hits[0].passage.text[:900] + " [1]"]
    return "Các dòng liên quan trong tài liệu:\n\n" + "\n".join(excerpts)


def best_sentence(question: str, passage: Passage, max_chars: int = 320) -> str:
    """Return the line/sentence of a passage that best matches the question."""
    query_terms = set(expanded_tokens(question))
    best, best_score = "", 0.0
    for line in passage.text.splitlines():
        for sentence in re.split(r"(?<=[.;:!?])\s+", line.strip()):
            sentence = re.sub(r"^[-*>#\s|]+", "", sentence).strip()
            if len(sentence) < 15:
                continue
            words = set(tokens(sentence))
            score = len(query_terms & words) / max(len(words), 1) ** 0.3
            if score > best_score:
                best, best_score = sentence, score
    return best[:max_chars]
