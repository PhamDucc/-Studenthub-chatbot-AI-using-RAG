"""Check a few source-backed completeness constraints before accepting a draft.

These checks use the retrieved evidence, not question IDs or stored test answers.
They request one correction; they never silently change the model's facts.
"""
import re

from ..models import Hit
from .retrieval import normalize


def _plain(text: str) -> str:
    return ' '.join(re.findall(r'[a-z0-9]+', normalize(text)))


def _course_rows(hits: list[Hit]):
    """Read block labels from detailed tables, excluding five-column study plans."""
    for hit in hits:
        block, role = None, None
        for line in hit.passage.text.splitlines():
            if not line.lstrip().startswith('|'):
                continue
            cells = [cell.strip().strip('*') for cell in line.strip().split('|')[1:-1]]
            if len(cells) < 8:
                continue
            label = cells[0].strip()
            if re.fullmatch(r'[IVX]+(?:\.\d+)*', label):
                block = next((name for name in ('II.1', 'II.2', 'IV', 'III', 'I')
                              if label == name or label.startswith(name + '.')), None)
                row_label = _plain(' '.join(cells[:3]))
                role = 'tự chọn' if 'tu chon' in row_label else 'bắt buộc' if 'bat buoc' in row_label else None
            elif block:
                for code in re.findall(r'UET\.[A-Z]+\d+', cells[1]):
                    yield hit.passage.source, code, block, role


def _conduct_minimums(hits: list[Hit]) -> dict[str, int]:
    minimums = {}
    for hit in hits:
        if hit.passage.source != 'Hoc_bong_va_diem_ren_luyen.md':
            continue
        for line in hit.passage.text.splitlines():
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if len(cells) >= 3:
                cell = _plain(cells[2])  # Conduct column, not the GPA column.
            elif len(cells) == 2 and _plain(cells[0]) in ('xuat sac', 'tot', 'kha'):
                cell = _plain(' '.join(cells))
            else:
                continue
            match = re.search(r'\b(xuat sac|tot|kha)\b[^0-9]*(\d{2,})', cell)
            if match:
                minimums[match[1]] = int(match[2])
    return minimums


def completeness_issues(question: str, hits: list[Hit], answer: str) -> list[str]:
    q, draft = _plain(question), _plain(answer)
    issues = []
    if re.search(r'\bdrl\b|ren luyen', q):
        minimums = _conduct_minimums(hits)
        raw = normalize(answer).replace('*', '')
        for match in re.finditer(r'\bloai (xuat sac|tot|kha)(?: tro len)?\s*\([^)]{0,15}?(?:≥|>=|\\geq?)\s*(\d+)', raw):
            line_start = raw.rfind('\n', 0, match.start()) + 1
            roles = list(re.finditer(r'\b(?:gpa|drl|diem ren luyen|ren luyen)\b', raw[line_start:match.start()]))
            if roles and roles[-1].group() == 'gpa':
                continue
            if not roles and match[1] != 'tot':
                continue  # Khá/Xuất sắc alone may label GPA rather than conduct.
            if match[1] in minimums and int(match[2]) != minimums[match[1]]:
                issues.append(f'Ngưỡng điểm rèn luyện loại {match[1]} trong bảng nguồn là {minimums[match[1]]}, '
                              f'khác ngưỡng {match[2]} đang ghi. Phân biệt ngưỡng phân loại ĐRL với '
                              'điều kiện tối thiểu xét học bổng; ghi đúng cả hai nếu nhắc đến.')
                break
        for match in re.finditer(r'\b(?:drl|diem ren luyen)\b[^\d\n]{0,30}(\d{1,3})(?!\d)'
                                 r'(?P<between>[^\n]{0,80}?)\bloai (xuat sac|tot|kha)\b(?! tro len)', raw):
            if re.search(r'hoc bong|gpa', match['between']):
                continue  # A scholarship level is not a conduct classification.
            score = int(match[1])
            eligible = [(label, minimum) for label, minimum in minimums.items() if minimum <= score <= 100]
            if eligible:
                expected, minimum = max(eligible, key=lambda item: item[1])
                claimed = match[3]
                if claimed != expected:
                    issues.append(f'Theo bảng ĐRL trong nguồn, {score} điểm xếp loại {expected} (từ {minimum}), '
                                  f'không phải loại {claimed}. Tách xếp loại ĐRL thực tế khỏi '
                                  'mức tối thiểu để được xét học bổng và mức học bổng sau khi lấy yếu tố thấp hơn.')
                    break
    curricula = [hit for hit in hits if hit.passage.source.startswith('CTDT_')]
    context = _plain('\n'.join(hit.passage.text for hit in curricula))
    course_blocks: dict[str, set[str]] = {}
    course_roles: dict[str, dict[str, str]] = {}
    for source, code, block, role in _course_rows(curricula):
        course_blocks.setdefault(code, set()).add(block)
        if role:
            course_roles.setdefault(code, {})[source] = role
    claimed_block = None
    for line in answer.splitlines():
        codes = re.findall(r'UET\.[A-Z]+\d+', line)
        heading = re.match(r'^\s*(?:#{1,6}\s+(.+)|(?:[-*]\s+)?\*\*([^*]+)\*\*)', line)
        title = (heading.group(1) or heading.group(2)) if heading else None
        if title and not re.search(r'UET\.[A-Z]+\d+', title):
            label = _plain(title)
            if 'co so nganh' in label:
                claimed_block = 'II.1'
            elif 'cot loi nganh' in label:
                claimed_block = 'II.2'
            elif 'thuc tap va tot nghiep' in label:
                claimed_block = 'IV'
            elif not codes and not re.search(r'bat buoc|tu chon|dinh huong', label):
                claimed_block = None
        if claimed_block:
            wrong = [code for code in codes
                     if code in course_blocks and claimed_block not in course_blocks[code]]
            if wrong:
                issues.append('Sai nhóm học phần: ' + ', '.join(wrong) + ' không thuộc nhóm ' + claimed_block
                              + ' đang dùng làm tiêu đề. Đối chiếu nhãn khối ở bảng nguồn; '
                                'tách học phần tốt nghiệp thuộc khối IV khỏi nhóm cốt lõi II.2/cơ sở II.1.')
                break
    shared_required = False
    for line in answer.splitlines():
        label = _plain(line)
        section = re.match(r'^\s*(?:[-*]\s+)?\*\*([^*]+)\*\*', line)
        new_section = section is not None and not re.search(r'UET\.[A-Z]+\d+', section.group(1))
        if new_section or line.lstrip().startswith('#') or re.search(r'diem khac biet|su khac biet|mon rieng', label):
            shared_required = False
        if re.search(r'ca hai.{0,100}bat buoc', label):
            shared_required = True
        if shared_required:
            for code in re.findall(r'UET\.[A-Z]+\d+', line):
                roles = course_roles.get(code, {})
                if len(roles) >= 2 and any(role != 'bắt buộc' for role in roles.values()):
                    issues.append('Danh sách nói bắt buộc ở cả hai ngành nhưng nguồn ghi '
                                  + code + ': ' + '; '.join(f'{source}: {role}' for source, role in roles.items())
                                  + '. Sửa bảng so sánh để ghi đúng vai trò từng ngành; cùng có môn không đồng nghĩa cùng bắt buộc. '
                                    'Kiểm tra cả các môn tự chọn khác, không giữ tiêu đề bắt buộc chung cho cả danh sách.')
                    shared_required = False
                    break
    if ('du an tot nghiep' in draft and re.search(r'khoi thay the.{0,1000}lua chon du 0?6 tin chi', context)
            and not re.search(r'\b0?6 (tin chi|tc)\b', draft)):
        issues.append('Nguồn quy định dự án tốt nghiệp đi kèm 06 tín chỉ học phần thay thế. '
                      'Nêu đủ hai thành phần của phương án này; không coi riêng dự án là thay toàn bộ đồ án/khóa luận.')
    program_codes = {}
    for hit in curricula:
        program_codes.setdefault(hit.passage.source, set()).update(re.findall(r'UET\.[A-Z]+\d+', hit.passage.text))
    if len(program_codes) >= 2 and re.search(r'hoc phan|mon|chuyen nganh|khoi kien thuc', q) and re.search(r'so sanh|khac|giong|trung', q):
        cited_codes = set(re.findall(r'UET\.[A-Z]+\d+', answer))
        if any(len(codes & cited_codes) < 2 for codes in program_codes.values()):
            issues.append('Câu hỏi so sánh học phần nhưng bản nháp chưa nêu học phần cụ thể của từng ngành. '
                          'Bổ sung ít nhất hai ví dụ tên và mã học phần từ bảng của MỖI ngành, '
                          'nêu phần chung và khác nhau, giữ đúng nhãn bắt buộc/tự chọn. Danh sách định hướng chưa đủ.')
    if re.search(r'(?:Σ|∑|sigma)\s*(?:\*|\||:|=|la|là|biểu thị| )*\s*(?:tổng số|số lượng) học phần', answer, re.I):
        issues.append('Chú giải sai phép tổng: Σ/∑ là ký hiệu lấy tổng, n mới là số học phần. '
                      'Giữ trung bình có trọng số và phân biệt phạm vi GPA/CPA theo Điều 42.')
    source_text = _plain('\n'.join(hit.passage.text for hit in hits))
    if (re.search(r'(?:cap lai|lam lai|mat)\b.{0,30}\bthe\b', q)
            and 'phat hanh lai the vat ly 50 000' in source_text):
        raw = normalize(answer).replace('*', '')
        for line in re.split(r'[\n;!?]', raw):
            if (re.search(r'30[., ]?000', line) and re.search(r'cap lai|lam lai|phat hanh lai', line)
                    and not re.search(r'thuong nien|khong phai|khong dung', line)):
                issues.append('30.000 đồng là phí thường niên, không phải phí phát hành lại. '
                              'Biểu phí chung BIDV từ 21/05/2025 ghi 50.000 đồng cho thẻ ghi nợ nội địa '
                              'vật lý khách hàng thông thường, chưa VAT; phải giữ phạm vi và ưu đãi cần xác nhận.')
                break
        if re.search(r'50[., ]?000', raw) and ('vat' not in raw or not re.search(r'xac nhan|uu dai|mien.giam|neu dung|neu ap dung', raw)):
            issues.append('Khi nêu 50.000 đồng, phải ghi đây là biểu phí BIDV chung chưa VAT và '
                          'cần xác nhận đúng sản phẩm/ưu đãi riêng; không coi là tổng tiền bắt buộc mọi sinh viên.')
    if ('hoc bong' in draft and 'thoi gian dao tao chuan' in source_text
            and re.search(r'thoi gian dao tao.{0,100}(?:chua|can xac nhan)', draft)):
        closing = re.search(r'(?:ket luan|tom lai)(.*)$', draft)
        if (closing and re.search(r'ban (?:da )?du dieu kien', closing[1])
                and not re.search(r'\bneu\b|voi dieu kien|can xac nhan|chua the|co dieu kien', closing[1])):
            issues.append('Phần kết luận phải giữ điều kiện còn thiếu đã nêu trong thân bài. '
                          'Chỉ xác nhận đạt các ngưỡng đã có dữ kiện; cần xác nhận thời gian đào tạo chuẩn '
                          'và chờ xét chỉ tiêu, không kết luận đủ mọi điều kiện khi còn thiếu dữ liệu.')
        for sentence in re.split(r'(?<=[.!?])\s+|\n', answer):
            claim = _plain(sentence)
            if (re.search(r'\bban (?:van |da )?du dieu kien\b', claim)
                    and not re.search(r'\bneu\b|voi dieu kien|can xac nhan|cac nguong|diem so|rieng ve', claim)):
                issues.append('Không khẳng định đủ điều kiện ở câu mở đầu rồi mới nêu điều kiện chưa biết ở dưới. '
                              'Nêu đạt các ngưỡng điểm/tín chỉ đã cung cấp và còn cần xác nhận thời gian đào tạo chuẩn, '
                              'kể cả khi kết luận cuối đã có điều kiện.')
                break
    if ('mien' in q and 'hoc phi' in q and 'ho ngheo' in q
            and re.search(r'neu.{0,80}khong thuoc.{0,40}(?:nhom doi tuong nay|nhom nay|dan toc thieu so)'
                          r'.{0,120}khong.{0,60}mien', draft)
            and not re.search(r'dien khac|doi tuong khac|cac nhom khac', draft)):
        issues.append('Hộ nghèo riêng lẻ chưa đủ, nhưng dân tộc thiểu số nghèo/cận nghèo chỉ là một diện miễn học phí. '
                      'Không kết luận ai ngoài nhóm đó đều không được miễn; nguồn còn các diện chính sách khác. '
                      'Hỏi diện chính sách và minh chứng phù hợp trước khi kết luận cá nhân.')
    if ('24 tin chi' in draft and 'mot hoac hai trong ba dieu kien' in source_text
            and not re.search(r'don vi|thu truong|tuy theo', draft)):
        issues.append('Ngưỡng F quá 24 tín chỉ là một tiêu chí cảnh báo do đơn vị lựa chọn áp dụng. '
                      'Nêu rõ thủ trưởng đơn vị quy định áp dụng một hoặc hai trong ba tiêu chí; '
                      'không trình bày ngưỡng như chế tài tự động cho mọi sinh viên.')
    coverage_context = (any(hit.passage.source == 'Pham_vi_du_lieu_can_doi_chieu.md' for hit in hits)
                        or 'danh ba khong chi dinh' in source_text)
    if ('ren luyen' in q and 'khong tu gan' in source_text
            and re.search(r'nha truong khong (?:tu gan|(?:quy dinh|an dinh|ban hanh|co)\b.{0,70}(?:diem|muc|co dinh))', draft)):
        issues.append('Hướng dẫn không tự gán điểm là giới hạn của câu trả lời khi thiếu bảng tiêu chí, '
                      'không phải quy định nhà trường không ấn định điểm cho từng hoạt động. '
                      'Nêu khung và ví dụ có nguồn, giữ phần mức điểm chi tiết cần bảng tiêu chí của đơn vị.')
    if coverage_context and 'ban ghi diem f sau hoc lai' in source_text:
        for sentence in re.split(r'[.!?;\n]', answer):
            statement = _plain(sentence)
            if (re.search(r'\bf(?: cu)?\b.{0,45}\b(?:van ton tai|con ton tai|van duoc luu|'
                          r'duoc xoa|bi xoa|khong bi xoa|khong duoc xoa)\b', statement)
                    and re.search(r'ho so|bang diem|ban ghi', statement)
                    and not re.search(r'chua xac dinh|chua du|khong the khang dinh|'
                                      r'khong dong nghia|khong hua|khong nen khang dinh', statement)):
                issues.append('Nguồn chưa xác nhận cách hiển thị F cũ trên từng loại bảng điểm. '
                              'Không khẳng định chắc chắn F luôn còn trong hồ sơ hoặc sẽ được xóa. '
                              'Nêu phần chưa xác định và yêu cầu Phòng Đào tạo xác nhận; '
                              'giữ quy định học lại đã có nguồn.')
                break
    if ('dieu 23 rut bot hoc phan' in source_text and 'diem f' in draft
            and re.search(r'qua (?:thoi )?han|ngoai thoi han', draft)
            and not re.search(r'khong (?:hoc|tham gia|di hoc)|bo hoc|bo mon|nghi hoc phan', draft)):
        issues.append('Điều 23 chỉ quy định nhận F khi quá hạn rút và sinh viên không học. '
                      'Giữ điều kiện không học/tự ý bỏ học; rút quá hạn không tự động làm '
                      'sinh viên vẫn học và dự thi nhận F.')
    if (coverage_context
            and re.search(r'(chua|khong) co (van ban|quy dinh|thong bao|thong tin (?:chinh thuc|xac minh))|'
                          r'nha truong chua cong bo|phong khong co hop thu', draft)
            and not re.search(r'kho tai lieu|nguon (duoc cung cap|hien co|da kiem)|tai lieu (hien co|duoc cung cap|da kiem)|qua doi chieu|danh ba', draft)):
        issues.append('Chỉ xác nhận giới hạn bằng chứng trong kho tài liệu/nguồn đã kiểm tra. '
                      'Sửa khẳng định “chưa có văn bản/quy định” thành “trong các tài liệu đã kiểm tra chưa tìm thấy…”. '
                      'Việc chưa tìm được không chứng minh nhà trường không có quy định.')
    return_to_study = (re.search(r'tro lai|tiep tuc', q) and re.search(r'bao luu|nghi hoc', q)
                       or re.search(r'(?:tro lai|quay lai|tiep tuc) (?:viec )?hoc', draft))
    if (return_to_study
            and '2 tuan truoc khi het thoi han' in source_text
            and 'it nhat 05 ngay lam viec' in source_text
            and re.search(r'(?:0?5|nam) ngay lam viec', draft)
            and not re.search(r'(?:0?2|hai) tuan', draft)):
        issues.append('Nguồn có hai mốc xin trở lại học: Điều 36 ghi chậm nhất 2 tuần trước khi hết hạn; '
                      'trang thủ tục ghi ít nhất 05 ngày làm việc. Nêu cả hai cùng nguồn và cần đơn vị xác nhận, '
                      'không chỉ đưa mốc muộn hơn làm hạn chắc chắn. Hướng dẫn chủ động nộp sớm.')
    if (return_to_study and '2 tuan truoc khi het thoi han' in source_text
            and re.search(r'(?:nen|chu dong|khuyen nghi).{0,60}(?:0?2|hai) tuan', draft)
            and not re.search(r'(?:quy che|dieu 36).{0,150}(?:0?2|hai) tuan|cham nhat (?:0?2|hai) tuan', draft)):
        issues.append('Mốc 2 tuần là yêu cầu của Điều 36 Quy chế, không chỉ là lời khuyên để xử lý kịp. '
                      'Gắn rõ mốc 2 tuần với Quy chế và mốc 05 ngày làm việc với trang thủ tục; '
                      'khuyên nộp trước cả hai, không tự tuyên bố mốc nào đã bị hủy.')
    if (any(hit.passage.source == 'Dang_ky_khoa_luan_CNTT_2026.md' for hit in hits)
            and re.search(r'(trung binh chung cac hoc phan|trung binh chung tich luy|cpa) tbc|'
                          r'tbc (la|tuong duong) (diem )?(trung binh chung cac hoc phan|trung binh chung tich luy|cpa)', draft)):
        issues.append('Bỏ phần diễn giải tên của TBC trong bản nháp. Dùng nguyên hai nhãn cột '
                      '“TBC tối thiểu” và “TCTL tối thiểu” như bảng thông báo. '
                      'Dẫn vào bảng bằng câu “Các ngưỡng được ghi trong thông báo theo từng khóa:”. '
                      'Giữ ngưỡng theo từng khóa và phạm vi đợt, tiên quyết CS3138 cùng phần cần hỏi thêm.')
    if ('hoc bong' in q and 'thi lai' in q and 'lan thu nhat' in source_text
            and ('thi lai' not in draft or not re.search(r'khong.{0,100}(thay|dung diem|lay diem)', draft))):
        issues.append('Trả lời riêng tình huống thi lại: điểm thi lại không thay điểm thi/kiểm tra hết môn lần thứ nhất '
                      'dùng xét học bổng. Phân biệt với học lại/cải thiện học phần và giữ các điều kiện chung.')
    if (re.search(r'khoa luan', q) and re.search(r'dieu kien|dang ky', q)
            and any('khoa luan' in _plain(line) and 'UET.CS3138' in line
                    for hit in curricula for line in hit.passage.text.splitlines())
            and 'CS3138' not in answer and 'thuc hanh nghien cuu' not in draft):
        issues.append('Dòng khóa luận trong CTĐT có tiên quyết UET.CS3138 (Thực hành nghiên cứu). '
                      'Nêu điều kiện tiên quyết đã biết và Điều 21.7; tách khỏi ngưỡng điểm/tín chỉ riêng theo khóa/đợt còn thiếu.')
    if (re.search(r'thu truong don vi dao tao\s*\(\s*khoa', normalize(answer))
            and any(hit.passage.source == 'Quy_che_dao_tao.md' for hit in hits)):
        issues.append('Giữ đúng thuật ngữ thủ trưởng đơn vị đào tạo trong Quy chế; không tự chú giải '
                      'đó là Khoa CNTT thuộc UET. Khoa là đầu mối nhận hướng dẫn/thông báo theo ngành, '
                      'không được tự đồng nhất với cấp đơn vị đào tạo trong điều khoản.')
    credit_limit = any('Điều 21.' in hit.passage.heading for hit in hits)
    if credit_limit:
        for sentence in re.split(r'(?<=[.!?])\s+|\n', answer):
            claim = _plain(sentence)
            if (re.search(r'\b\d{2,}(?:[,.]\d+)?\s*(?:tin chi\s*)?/\s*\d+', normalize(sentence))
                    and not re.search(r'khong (?:duoc |nen )?(?:lay|chia)|tranh (?:lay|chia)', claim)):
                issues.append('Không tính khối lượng trung bình hợp lệ hay trần đăng ký bằng cách chia thẳng '
                              'tổng tín chỉ CTĐT cho số kỳ, kể cả khi gọi là trần lý thuyết rồi thêm lưu ý. '
                              'Bỏ các kết quả số từ phép chia đó; chỉ nêu công thức 3/2 khối lượng trung bình '
                              'hợp lệ và phần dữ liệu kế hoạch còn thiếu sau các loại trừ Điều 21.')
                break
            if (re.search(r'ngoai nguong|ngoai.{0,25}quy dinh|vuot.{0,25}(?:toi da|tran)', claim)
                    and re.search(r'dong y|phe duyet|chap thuan', claim)
                    and re.search(r'thu truong|hieu truong', claim)
                    and not re.search(r'it hon|duoi.{0,15}toi thieu|khong (?:co|cho phep|duoc)', claim)):
                issues.append('Điều 21 chỉ cho thủ trưởng đồng ý đăng ký ít hơn mức tối thiểu. '
                              'Không mở rộng thành quyền cho phép đăng ký ngoài mọi ngưỡng hoặc vượt trần tối đa. '
                              'Giữ công thức trần và ngoại lệ học kỳ cuối đúng nguồn.')
                break
    duration_question = re.search(r'\bmay ky\b|\bso (?:hoc )?ky (?:it nhat|toi thieu)\b|'
                                 r'\b(?:it nhat|toi thieu) (?:bao nhieu |may )?(?:hoc )?ky\b|'
                                 r'\b\d+ (?:hoc )?ky\b.{0,45}(?:ra truong|tot nghiep)', q)
    if credit_limit and duration_question and ('tin chi' in q or curricula):
        exclusions = ('giao duc the chat', 'giao duc quoc phong', 'ky nang bo tro', 'cai thien', 'tu chon tu do')
        raw = normalize(answer).replace('*', '')
        total_division = re.search(r'\b\d{2,}(?:[,.]\d+)?\s*(?:tin chi\s*)?/\s*\d+', raw)
        if not all(term in draft for term in exclusions) or total_division:
            issues.append('Ước lượng số kỳ chưa tuân thủ phạm vi Điều 21.1. Nêu đủ các loại học phần bị loại trừ '
                          '(GDTC, GDQP-AN, kỹ năng bổ trợ, cải thiện, tự chọn tự do) và ngoại lệ học kỳ cuối. '
                          'Chưa xác định được khối lượng trung bình hợp lệ sau các loại trừ nên chưa thể chốt '
                          'một số kỳ tối thiểu hoặc trần tín chỉ cố định. Giữ tổng tín chỉ và thời gian chuẩn có nguồn, '
                          'nêu công thức trần 1,5 lần khối lượng trung bình hợp lệ; bỏ phép lấy tổng CTĐT chia số kỳ '
                          'để áp trần và bỏ kết luận số kỳ từ phép chia đó. Còn phụ thuộc tiên quyết, lịch mở môn, điều kiện tốt nghiệp.')
    return issues
