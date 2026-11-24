# Dữ liệu đánh giá bộ 95 câu

Thư mục này chứa dữ liệu dùng để kiểm tra và chấm bộ 95 câu hỏi StudentHub UET.

## Nội dung

- `cases.json`: danh sách 95 câu hỏi, tài liệu mục tiêu và nhãn ngoài phạm vi.
- `final-attempts.jsonl`: các lần gọi chatbot thực tế, gồm đáp án, nguồn truy xuất, thời gian, mode và lỗi nếu có. Tệp giữ nhiều lần thử của một câu để không xóa lịch sử lỗi.
- `review-01-35.json`, `review-36-66.json`, `review-67-95.json`: nhận xét thủ công, mức độ lỗi, cách sửa kỳ vọng và bằng chứng nguồn của lượt đánh giá ban đầu.
- [q95-metric-scores.md](../q95-metric-scores.md): phương pháp và kết quả chấm metric.
- [q95-metric-scores.csv](../q95-metric-scores.csv): bảng điểm dạng CSV.

## Lưu ý

Các điểm `source_safe_handling` và `answer_relevance` hiện là proxy từ đánh giá thủ công, chưa phải kết quả RAGAS hoặc LLM judge độc lập. Điểm tổng hợp 93,16/100 sử dụng quy tắc riêng được mô tả trong báo cáo metric.
