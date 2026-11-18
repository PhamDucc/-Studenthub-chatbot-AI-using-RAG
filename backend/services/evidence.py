"""Assemble complete, source-scoped evidence for multipart academic questions.

The vector index stays unchanged. These views retain original rows and section
boundaries, so a long table cannot lose its totals or mandatory/elective labels.
"""

from functools import lru_cache
import re

from ..config import DATA_DIR
from ..models import Hit, Passage
from ..repositories.documents import data_signature
from .retrieval import normalize


PROGRAMS = {
    'CTDT_CNTT.md': ('công nghệ thông tin', 'information technology'),
    'CTDT_KHMT.md': ('khoa học máy tính', 'computer science'),
    'CTDT_HTTT.md': ('hệ thống thông tin', 'information systems'),
    'CTDT_An_toan_thong_tin.md': ('an toàn thông tin', 'information security'),
    'CTDT_MMT&TTDL.md': ('mạng máy tính và truyền thông dữ liệu', 'mạng máy tính', 'computer networks'),
    'CTDT_Tri_tue_nhan_tao.md': ('trí tuệ nhân tạo', 'artificial intelligence'),
    'CTDT_Khoa_hoc_du_lieu.md': ('khoa học dữ liệu', 'khoa học và kỹ thuật dữ liệu', 'data science'),
    'CTDT_KTMT.md': ('kỹ thuật máy tính', 'computer engineering'),
    'CTDT_KTĐTVT.md': ('kỹ thuật điện tử viễn thông', 'điện tử viễn thông', 'electronics and telecommunications'),
    'CTDT_Ky_thuat_co_dien_tu.md': ('kỹ thuật cơ điện tử', 'cơ điện tử', 'mechatronics'),
    'CTDT_Ky_thuat_dieu_khien_va_tu_dong_hoa.md': ('kỹ thuật điều khiển và tự động hóa', 'tự động hóa', 'automation'),
    'CTDT_KTRobot.md': ('kỹ thuật robot', 'robot'),
    'CTDT_VLKT.md': ('vật lý kỹ thuật', 'engineering physics'),
    'CTDT_Ky_thuat_vat_lieu_va_vi_dien_tu.md': ('kỹ thuật vật liệu và vi điện tử', 'vật liệu và vi điện tử'),
    'CTDT_Co_ky_thuat.md': ('cơ kỹ thuật', 'engineering mechanics'),
    'CTDT_Ky_thuat_hang_khong_vu_tru.md': ('kỹ thuật hàng không vũ trụ', 'hàng không vũ trụ', 'aerospace'),
    'CTDT_Ky_thuat_xay_dung.md': ('kỹ thuật xây dựng', 'civil engineering'),
    'CTDT_Cong_nghe_ky_thuat_sinh_hoc.md': ('công nghệ kỹ thuật sinh học', 'công nghệ sinh học'),
    'CTDT_Cong_nghe_nong_nghiep.md': ('công nghệ nông nghiệp', 'agricultural technology'),
    'CTDT_KTNL.md': ('kỹ thuật năng lượng', 'energy engineering'),
    'CTDT_Thiet_ke_cong_nghiep_va_do_hoa.md': ('thiết kế công nghiệp và đồ họa', 'thiết kế đồ họa', 'graphic design'),
}


def _plain(text: str) -> str:
    return ' '.join(re.findall(r'[a-z0-9]+', normalize(text)))


def named_programs(question: str) -> list[str]:
    query = ' ' + _plain(question) + ' '
    return [source for source, aliases in PROGRAMS.items()
            if any(' ' + _plain(alias) + ' ' in query for alias in aliases)]


def _transfer_request(question: str) -> bool:
    # Accent folding makes "chuyên ngành" and "chuyển ngành" identical.
    # Use the original phrase or a transfer verb before reserving legal context.
    q = _plain(question)
    return ('chuyển ngành' in question.casefold() or 'chuyển chương trình' in question.casefold()
            or bool(re.search(r'chuyen sang|xin chuyen|dieu kien chuyen|thu tuc chuyen', q))
            or bool(re.match(r'^chuyen (nganh|chuong trinh)', q)))


@lru_cache(maxsize=2)
def _texts(signature: tuple) -> dict[str, list[str]]:
    return {name: (DATA_DIR / name).read_text(encoding='utf-8').splitlines() for name, _, _ in signature}


def _program_view(source: str, question: str, lines: list[str]) -> Hit:
    query = _plain(question)
    # Overview (PEO, PLO and actual job titles) ends before summary/course tables.
    summary = next((i for i, line in enumerate(lines) if 'tom tat chuong trinh' in _plain(line)), len(lines))
    table = next((i for i, line in enumerate(lines)
                  if 'ma hoc phan' in _plain(line) and line.lstrip().startswith('|')), len(lines))
    plan = next((i for i, line in enumerate(lines) if 'bang tien trinh' in _plain(line)), len(lines))
    # Some documents put the study plan before the detailed framework.
    core_end = next((i for i in range(table + 1, len(lines))
                     if lines[i].startswith('#') and 'chuong trinh dao tao' in _plain(lines[i])), len(lines))
    if table < plan:
        core_end = min(core_end, plan)

    overview = bool(re.search(r'\b(muc tieu|chuan dau ra|ky nang|ngoai ngu|vi tri|cong viec|dam nhan|viec lam|nghe nghiep|nghe gi|lam nghe|ra truong|career|outcome)\b', query))
    courses = bool(re.search(r'hoc phan|mon|chuyen nganh|chuyen sau|dinh huong|co so nganh|cot loi|tu chon|bat buoc|do an|khoa luan|studio|thuc tap|so sanh|khac|trung|\b(?:co day|day ve|co hoc|hoc ve|teach|teaches|cover)\b', query))
    schedule = bool(re.search(r'lo trinh|hoc ky|nam nhat|phan bo|studio|do an|thuc hanh|thuc tap', query))
    selected: set[int] = set()
    # Always keep totals, standard duration and exclusion notes, even if the
    # lexical top hits happened to be late-semester study-plan fragments.
    for i, line in enumerate(lines):
        text = _plain(line)
        if 'tong so tin chi' in text and not schedule:
            continue  # Don't detach semester subtotals from their semester labels.
        if ('thoi gian dao tao' in text or 'tong cong' in text or 'tong ' in text
                or 'khong duoc tinh vao tong' in text):
            selected.add(i)
    if summary < table:
        selected.update(range(summary, table))

    if overview:
        selected.update(range(0, min(summary, table, plan)))
    if courses and table < len(lines):
        base_only = 'co so nganh' in query and not re.search(r'cot loi|chuyen sau|dinh huong|chuyen nganh', query)
        base_start = next((i for i in range(table, core_end)
                           if re.match(r'^\|\s*\*{0,2}II\.1\*{0,2}\s*\|', lines[i])), None)
        if base_only and base_start is not None:
            base_end = next((i for i in range(base_start + 1, core_end)
                             if re.match(r'^\|\s*\*{0,2}(?:II\.2|III|IV)\*{0,2}\s*\|', lines[i])), core_end)
            selected.update(range(table, min(table + 2, core_end)))
            selected.update(range(base_start, base_end))
        else:
            selected.update(range(table, core_end))
    if schedule and plan < len(lines):
        # Stop at a subsequent full curriculum heading when plans occur first.
        end = next((i for i in range(plan + 1, len(lines))
                    if lines[i].startswith('#') and 'chuong trinh dao tao' in _plain(lines[i])), len(lines))
        selected.update(range(plan, end))
    # Headers/row labels are preserved verbatim; no generated course facts.
    text = '\n'.join(lines[i] for i in sorted(selected)).strip()
    title = PROGRAMS[source][0]
    return Hit(Passage(source, title, f'CTĐT {title}: tổng tín chỉ, khối kiến thức và các mục liên quan', text), 1.0)


def _policy_sources(question: str) -> dict[str, list[str]]:
    """Select related legal/procedural sections for every requested subject."""
    q = _plain(question)
    rules: dict[str, list[str]] = {}
    def add(source: str, *headings: str):
        rules.setdefault(source, []).extend(headings)

    if re.search(r'quy doi|diem chu|he 10|he 4|thang diem 4', q):
        add('Quy_che_dao_tao.md', 'Điều 41.', 'Điều 43.')
    if re.search(r'diem trung binh|gpa|cpa', q):
        add('Quy_che_dao_tao.md', 'Điều 42.', 'Điều 43.')
        if re.search(r'dang ky|ky toi|hoc ky toi|\btin\b|\btc\b|tin chi', q):
            add('Quy_che_dao_tao.md', 'Điều 21.', 'Điều 23.', 'Điều 44.')
        if re.search(r'xep loai|hoc luc|xuat sac', q):
            add('Quy_che_dao_tao.md', 'Điều 45.')
    if re.search(r'canh bao|hoc vu|diem f|tach mon|hoc lai|thi lai', q):
        add('Quy_che_dao_tao.md', 'Điều 21.', 'Điều 42.', 'Điều 44.')
    if re.search(r'hoc cai thien|cai thien diem', q):
        add('Quy_che_dao_tao.md', 'Điều 21.', 'Điều 42.')
        if 'hoc phi' in q:
            add('Quy_dinh_ve_hoc_phi.md', '2. Học phí học lại')
    if re.search(r'chuan dau ra', q) and re.search(r'ngoai ngu|tin hoc', q):
        add('Quy_che_dao_tao.md', 'Điều 13.', 'Điều 46.')
    if re.search(r'tot nghiep|ra truong', q) and re.search(r'dieu kien|cong nhan|ky luat|chac chan|duoc|bao nhieu|\bcon\b', q):
        add('Quy_che_dao_tao.md', 'Điều 46.')
        add('Khen_thuong_ky_luat.md', 'PHẦN II')
    if _transfer_request(question):
        add('Quy_che_dao_tao.md', 'Điều 27.', 'Điều 28.', 'Điều 42.')
    if ('hoc bong' not in q and
            ((re.search(r'\b(tin chi|tin|tc)\b', q) and re.search(r'dang ky|toi da|toi thieu|it nhat may ky|ky toi', q))
             or ('dang ky' in q and re.search(r'moi ky|hoc ky|het muc|toi da', q)))):
        add('Quy_che_dao_tao.md', 'Điều 21.')
    if re.search(r'nghi hoc|bao luu|tam dung (viec )?hoc', q):
        add('Quy_che_dao_tao.md', 'Điều 36.', 'Điều 17.')
        add('Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md', '10. Xin nghỉ học', '11. Đơn xin tiếp tục')
    if re.search(r'rut hoc phan|rut bot|bo bot|huy hoc phan|hoan tra|hoan phi|hoan hoc phi', q):
        add('Quy_che_dao_tao.md', 'Điều 23.')
    if 'ky luat' in q and re.search(r'sau bao lau|xoa|cham dut|ho so', q):
        add('Khen_thuong_ky_luat.md', '2. Chấm dứt hiệu lực')
    if 'hoc bong' in q and re.search(r'hoc lai|thi lai|cai thien|tin chi|\bgpa\b|\bcpa\b|\bdrl\b', q):
        add('Hoc_bong_va_diem_ren_luyen.md', 'PHẦN I')
    if re.search(r'nghien cuu khoa hoc|olympic', q):
        add('Quy_che_dao_tao.md', 'Điều 32.', 'Điều 27.')
        add('Khen_thuong_ky_luat.md', 'PHẦN I')
    if re.search(r'khoa luan|do an tot nghiep', q):
        add('Quy_che_dao_tao.md', 'Điều 21.')
        if any(source in named_programs(question) for source in ('CTDT_KHMT.md', 'CTDT_CNTT.md', 'CTDT_HTTT.md', 'CTDT_MMT&TTDL.md')):
            add('Dang_ky_khoa_luan_CNTT_2026.md', 'Điều kiện', 'Phạm vi', 'Thủ tục')
    if re.search(r'phong dao tao|chuyen nganh|canh bao|diem f|tach mon', q):
        add('Thong_tin_lien_he_voi_nha_truong.md', '2. Phòng Đào tạo')
    if re.search(r'ke hoach tai chinh|khtc|bien lai', q):
        add('Thong_tin_lien_he_voi_nha_truong.md', '5. Phòng Kế hoạch')
    if re.search(r'cap lai the|mat the', q):
        add('Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md', '8. Xin cấp lại thẻ')
        add('Thong_tin_lien_he_voi_nha_truong.md', '1. Phòng Công tác')
    if re.search(r'mot cua|gio tiep|khung gio', q):
        add('Thong_tin_lien_he_voi_nha_truong.md', '6. Giờ tiếp nhận')
        add('Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md', '2. Xin cấp bảng điểm')
    # Coverage notes describe what remains unknown; they are never a new rule.
    coverage = [
        (r'canh bao', 'Cảnh báo'), (r'ngoai ngu|tin hoc', 'Tin học'),
        (r'bao luu|nghi hoc', 'Bảo lưu'), (r'hoan.*(hoc phi|phi)', 'Hoàn học phí'),
        (r'cap lai the|mat the', 'Phí cấp lại thẻ'), (r'gio tiep|khung gio|mot cua', 'Giờ một cửa'),
        (r'bang diem|diem f|tach mon', 'Bản ghi điểm F'), (r'khoa luan', 'Điều kiện khóa luận'),
        (r'ly thuyet.*thuc hanh|thuc hanh.*ly thuyet', 'Giờ học và tín chỉ'),
    ]
    for pattern, heading in coverage:
        if re.search(pattern, q):
            add('Pham_vi_du_lieu_can_doi_chieu.md', heading)
    if 'hoc phi' in q:
        exemption = bool(re.search(r'mien|giam', q))
        if exemption:
            add('Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md', '6. Xin xác nhận trợ cấp')
        if not exemption and re.search(r'muon|cham|no hoc phi|con no|thoi han|han ', q):
            add('Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md', '5. Xin nộp học phí muộn')
        if re.search(r'muon|cham|no hoc phi|con no|xu ly', q):
            add('Khen_thuong_ky_luat.md', 'PHẦN III', 'Phụ lục', 'vi phạm')
            add('Quy_che_dao_tao.md', 'Điều 38.')
        if re.search(r'khac|so sanh|muc|khoa hoc du lieu', q):
            add('Quy_dinh_ve_hoc_phi.md', 'III.', 'Bổ sung học phí')
    if 'ky luat' in q and re.search(r'hoc bong|tot nghiep|quyen loi', q):
        add('Khen_thuong_ky_luat.md', 'PHẦN II')
        add('Hoc_bong_va_diem_ren_luyen.md', '1. Đối tượng')
    if 'ren luyen' in q and re.search(r'cong|tru|hoat dong|khieu nai|quy trinh|yeu|kem', q):
        add('Hoc_bong_va_diem_ren_luyen.md', 'Bổ sung quy trình', 'Bổ sung hoạt động', '1. Nguyên tắc')
    if 'ren luyen' in q and re.search(r'khung|phan loai|xep loai|moc diem', q):
        add('Hoc_bong_va_diem_ren_luyen.md', '2. Khung phân loại')
    if re.search(r'giay xac nhan|vay von|nghia vu quan su', q):
        add('Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md', 'Giấy xác nhận', 'giấy xác nhận', '7. Xin xác nhận')
    return rules


def _program_parts(view: Hit) -> list[Hit]:
    """Keep the original publication parts as independently citable sources.

    Each curriculum combines several source pages. A single citation ID over
    all three pages invited the model to cite their part numbers instead.
    """
    sections = re.split(r'(?m)(?=^## Phần \d+:)', view.passage.text)
    if len(sections) > 1 and not sections[0].startswith('## Phần '):
        sections[1] = sections[0] + sections[1]
        sections = sections[1:]
    result = []
    for section in sections:
        if not section.strip():
            continue
        heading = next((line.removeprefix('## ') for line in section.splitlines()
                        if line.startswith('## Phần ')), 'Thông tin chương trình')
        result.append(Hit(Passage(view.passage.source, view.passage.title,
                                  f'CTĐT {view.passage.title}: {heading}', section.strip()), view.score))
    return result


def complete_evidence(question: str, ranked: list[Hit], passages: list[Passage], limit: int) -> list[Hit]:
    """Reserve context for named curricula and every explicitly requested policy."""
    query = _plain(question)
    # Preserve the specialised prerequisite path, and don't turn admission or
    # non-existent-program questions into invented curriculum answers.
    if 'y da khoa' in query:
        return []
    if re.search(r'tien quyet|prerequisite|diem chuan|tuyen sinh|xet tuyen', query):
        return ranked[:limit]
    docs = _texts(data_signature())
    sources = named_programs(question)
    if len(sources) == 1 and re.search(r'cac nganh ky thuat khac', query):
        # An unnamed comparison still needs actual comparison evidence. Use
        # representative engineering curricula; the answer must name them.
        peers = [source for source, aliases in PROGRAMS.items()
                 if source not in sources and source in docs and aliases[0].startswith('kỹ thuật')]
        sources.extend(peers[:2])
    structured = [part for source in sources if source in docs and not _transfer_request(question)
                  for part in _program_parts(_program_view(source, question, docs[source]))]
    policy = _policy_sources(question)
    for source, headings in policy.items():
        selected = [p for p in passages if p.source == source
                    and any(' ' + _plain(heading) + ' ' in ' ' + _plain(p.heading) + ' '
                            for heading in headings)]
        if not selected:
            continue
        text = '\n\n'.join(f'### {p.heading}\n{p.text}' for p in selected)
        actual_headings = list(dict.fromkeys(p.heading for p in selected))
        structured.append(Hit(Passage(source, selected[0].title, ' | '.join(actual_headings), text), 1.0))
    if not structured:
        return ranked[:limit]
    represented = {hit.passage.source for hit in structured}
    # Keep original snippets from other sources, not duplicate/truncated pieces
    # of the document view already supplied above.
    remaining = [hit for hit in ranked if hit.passage.source not in represented
                 and (not sources or not hit.passage.source.startswith('CTDT_'))]
    return (structured + remaining)[:limit]
