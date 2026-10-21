export const student = {
  name: 'Nguyễn Minh Anh',
  shortName: 'Minh Anh',
  initials: 'MA',
  studentId: '22021234',
  email: '22021234@vnu.edu.vn',
  phone: '0912 345 678',
  dob: '15/03/2004',
  gender: 'Nữ',
  hometown: 'Hà Nội',
  faculty: 'Khoa Công nghệ Thông tin',
  major: 'Khoa học Máy tính',
  className: 'K67-CA-CLC2',
  cohort: 'QH-2022-I/CQ',
  program: 'Chất lượng cao',
  advisor: 'TS. Trần Văn Hùng',
  status: 'Đang học',
  semester: 'Học kỳ I, năm học 2026–2027',
  gpa: 3.52,
  credits: 98,
  totalCredits: 150,
  ranking: 'Giỏi',
  currentCourses: 6,
}

export type ClassSession = {
  id: string
  code: string
  name: string
  room: string
  lecturer: string
  day: number
  startPeriod: number
  periods: number
  type: 'Lý thuyết' | 'Thực hành'
  color: 'navy' | 'sky' | 'amber' | 'emerald' | 'rose' | 'violet'
}

export const periods = [
  { period: 1, time: '07:00' },
  { period: 2, time: '08:00' },
  { period: 3, time: '09:00' },
  { period: 4, time: '10:00' },
  { period: 5, time: '11:00' },
  { period: 6, time: '12:00' },
  { period: 7, time: '13:00' },
  { period: 8, time: '14:00' },
  { period: 9, time: '15:00' },
  { period: 10, time: '16:00' },
  { period: 11, time: '17:00' },
  { period: 12, time: '18:00' },
]

export const weekDays = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7']

export const timetable: ClassSession[] = [
  { id: 's1', code: 'INT3401', name: 'Trí tuệ nhân tạo', room: '301-G2', lecturer: 'PGS.TS. Lê Thanh Hà', day: 0, startPeriod: 1, periods: 3, type: 'Lý thuyết', color: 'navy' },
  { id: 's2', code: 'INT3306', name: 'Phát triển ứng dụng Web', room: '208-E3', lecturer: 'TS. Hoàng Xuân Tùng', day: 0, startPeriod: 7, periods: 2, type: 'Lý thuyết', color: 'sky' },
  { id: 's3', code: 'INT3110', name: 'Phân tích và thiết kế hướng đối tượng', room: '102-G2', lecturer: 'TS. Đặng Đức Hạnh', day: 1, startPeriod: 2, periods: 3, type: 'Lý thuyết', color: 'emerald' },
  { id: 's4', code: 'INT3306', name: 'Phát triển ứng dụng Web', room: 'PM 207-G2', lecturer: 'ThS. Nguyễn Văn Nam', day: 1, startPeriod: 8, periods: 3, type: 'Thực hành', color: 'sky' },
  { id: 's5', code: 'INT3209', name: 'Khai phá dữ liệu', room: '309-GĐ3', lecturer: 'TS. Trần Mai Vũ', day: 2, startPeriod: 1, periods: 2, type: 'Lý thuyết', color: 'amber' },
  { id: 's6', code: 'INT3401', name: 'Trí tuệ nhân tạo', room: 'PM 313-G2', lecturer: 'ThS. Phạm Thu Trang', day: 2, startPeriod: 7, periods: 2, type: 'Thực hành', color: 'navy' },
  { id: 's7', code: 'INT3117', name: 'Kiểm thử và đảm bảo chất lượng phần mềm', room: '205-E3', lecturer: 'PGS.TS. Phạm Ngọc Hùng', day: 3, startPeriod: 3, periods: 3, type: 'Lý thuyết', color: 'rose' },
  { id: 's8', code: 'PHI1002', name: 'Chủ nghĩa xã hội khoa học', room: 'Hội trường G2', lecturer: 'TS. Vũ Thị Lan', day: 4, startPeriod: 1, periods: 2, type: 'Lý thuyết', color: 'violet' },
  { id: 's9', code: 'INT3209', name: 'Khai phá dữ liệu', room: 'PM 208-G2', lecturer: 'ThS. Lê Hoàng Quân', day: 4, startPeriod: 8, periods: 2, type: 'Thực hành', color: 'amber' },
  { id: 's10', code: 'INT3110', name: 'Phân tích và thiết kế hướng đối tượng', room: '102-G2', lecturer: 'TS. Đặng Đức Hạnh', day: 5, startPeriod: 2, periods: 2, type: 'Lý thuyết', color: 'emerald' },
]

export const upcomingClasses = [
  { id: 'u1', code: 'INT3401', name: 'Trí tuệ nhân tạo', time: '07:00 – 09:50', day: 'Hôm nay', room: '301-G2', lecturer: 'PGS.TS. Lê Thanh Hà', status: 'Sắp diễn ra' },
  { id: 'u2', code: 'INT3306', name: 'Phát triển ứng dụng Web', time: '13:00 – 14:50', day: 'Hôm nay', room: '208-E3', lecturer: 'TS. Hoàng Xuân Tùng', status: 'Chiều nay' },
  { id: 'u3', code: 'INT3110', name: 'Phân tích và thiết kế hướng đối tượng', time: '08:00 – 10:50', day: 'Ngày mai', room: '102-G2', lecturer: 'TS. Đặng Đức Hạnh', status: 'Ngày mai' },
  { id: 'u4', code: 'INT3306', name: 'Phát triển ứng dụng Web (TH)', time: '14:00 – 16:50', day: 'Ngày mai', room: 'PM 207-G2', lecturer: 'ThS. Nguyễn Văn Nam', status: 'Ngày mai' },
]

export const announcements = [
  { id: 'a1', category: 'Đào tạo', title: 'Thông báo lịch đăng ký học phần học kỳ II năm học 2026–2027', date: '20/10/2026', important: true },
  { id: 'a2', category: 'Tài chính', title: 'Hạn cuối nộp học phí học kỳ I: 31/10/2026', date: '18/10/2026', important: true },
  { id: 'a3', category: 'Khảo thí', title: 'Lịch thi giữa kỳ các học phần khối ngành Công nghệ Thông tin', date: '15/10/2026', important: false },
  { id: 'a4', category: 'Công tác SV', title: 'Mở đơn xét học bổng khuyến khích học tập học kỳ II năm 2025–2026', date: '12/10/2026', important: false },
  { id: 'a5', category: 'Sự kiện', title: 'UET Tech Day 2026 – Ngày hội công nghệ và việc làm', date: '10/10/2026', important: false },
]

export const academicRecords = [
  { semester: 'HK I 2022–2023', gpa: 3.21, credits: 18 },
  { semester: 'HK II 2022–2023', gpa: 3.38, credits: 20 },
  { semester: 'HK I 2023–2024', gpa: 3.55, credits: 19 },
  { semester: 'HK II 2023–2024', gpa: 3.62, credits: 21 },
  { semester: 'HK I 2025–2026', gpa: 3.68, credits: 20 },
]

export const currentCourses = [
  { code: 'INT3401', name: 'Trí tuệ nhân tạo', credits: 3, group: 'INT3401 2' },
  { code: 'INT3306', name: 'Phát triển ứng dụng Web', credits: 3, group: 'INT3306 1' },
  { code: 'INT3110', name: 'Phân tích và thiết kế hướng đối tượng', credits: 3, group: 'INT3110 3' },
  { code: 'INT3209', name: 'Khai phá dữ liệu', credits: 3, group: 'INT3209 1' },
  { code: 'INT3117', name: 'Kiểm thử và đảm bảo chất lượng phần mềm', credits: 3, group: 'INT3117 2' },
  { code: 'PHI1002', name: 'Chủ nghĩa xã hội khoa học', credits: 2, group: 'PHI1002 5' },
]

export const requestTypes = [
  { value: 'xac-nhan-sv', label: 'Giấy xác nhận sinh viên', fee: 'Miễn phí', days: '2 ngày làm việc' },
  { value: 'bang-diem', label: 'Bảng điểm (bản sao có dấu)', fee: '20.000đ / bản', days: '3 ngày làm việc' },
  { value: 'hoan-thi', label: 'Đơn xin hoãn thi', fee: 'Miễn phí', days: '5 ngày làm việc' },
  { value: 'nghi-hoc', label: 'Đơn xin nghỉ học tạm thời', fee: 'Miễn phí', days: '7 ngày làm việc' },
  { value: 'phuc-khao', label: 'Đơn phúc khảo bài thi', fee: '30.000đ / môn', days: '10 ngày làm việc' },
  { value: 'mien-giam', label: 'Đơn miễn giảm học phí', fee: 'Miễn phí', days: '10 ngày làm việc' },
]

export type ServiceRequest = {
  id: string
  type: string
  submittedAt: string
  status: 'Đang xử lý' | 'Đã duyệt' | 'Hoàn thành' | 'Từ chối'
  copies: number
}

export const requestHistory: ServiceRequest[] = [
  { id: 'DV-2026-0412', type: 'Giấy xác nhận sinh viên', submittedAt: '14/10/2026', status: 'Hoàn thành', copies: 2 },
  { id: 'DV-2026-0388', type: 'Bảng điểm (bản sao có dấu)', submittedAt: '02/10/2026', status: 'Đã duyệt', copies: 1 },
  { id: 'DV-2026-0217', type: 'Đơn phúc khảo bài thi', submittedAt: '18/07/2026', status: 'Từ chối', copies: 1 },
]

export const faqs = [
  { category: 'Đào tạo', q: 'Khi nào mở cổng đăng ký học phần?', a: 'Cổng đăng ký học phần thường mở 2–3 tuần trước khi bắt đầu học kỳ mới. Lịch cụ thể được công bố trên mục Thông báo và gửi qua email VNU của sinh viên.' },
  { category: 'Đào tạo', q: 'Số tín chỉ tối thiểu và tối đa mỗi học kỳ là bao nhiêu?', a: 'Sinh viên đăng ký tối thiểu 14 tín chỉ và tối đa 28 tín chỉ mỗi học kỳ chính. Sinh viên đang bị cảnh báo học vụ chỉ được đăng ký tối đa 18 tín chỉ.' },
  { category: 'Tài chính', q: 'Tôi có thể nộp học phí bằng những hình thức nào?', a: 'Học phí có thể nộp qua chuyển khoản ngân hàng liên kết (BIDV, Vietcombank), ví điện tử hoặc trực tiếp tại Phòng Kế hoạch – Tài chính. Nội dung chuyển khoản cần ghi rõ mã sinh viên.' },
  { category: 'Tài chính', q: 'Nộp học phí trễ hạn có bị phạt không?', a: 'Sinh viên nộp trễ hạn có thể bị tạm khóa tài khoản đăng ký học phần và không được dự thi cuối kỳ cho đến khi hoàn tất nghĩa vụ học phí.' },
  { category: 'Dịch vụ', q: 'Làm thế nào để xin giấy xác nhận sinh viên?', a: 'Vào mục Đơn từ & Dịch vụ công, chọn loại "Giấy xác nhận sinh viên", điền mục đích sử dụng và gửi đơn. Bạn sẽ nhận được thông báo khi giấy sẵn sàng để nhận tại Phòng Công tác Sinh viên.' },
  { category: 'Dịch vụ', q: 'Tôi theo dõi trạng thái đơn đã nộp ở đâu?', a: 'Toàn bộ đơn đã nộp được hiển thị trong phần "Lịch sử yêu cầu" tại trang Đơn từ & Dịch vụ công, kèm trạng thái xử lý được cập nhật theo thời gian thực.' },
  { category: 'Tài khoản', q: 'Tôi quên mật khẩu đăng nhập thì phải làm gì?', a: 'Chọn "Quên mật khẩu" tại trang đăng nhập và làm theo hướng dẫn gửi về email VNU. Nếu không nhận được email, liên hệ Trung tâm Máy tính, phòng 104-E3.' },
  { category: 'Khảo thí', q: 'Phúc khảo bài thi được thực hiện trong bao lâu?', a: 'Đơn phúc khảo cần nộp trong vòng 7 ngày kể từ ngày công bố điểm. Kết quả phúc khảo được trả trong khoảng 10 ngày làm việc.' },
]
