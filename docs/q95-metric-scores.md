# Điểm đánh giá metric cho bộ 95 câu hỏi

## 1. Phạm vi đánh giá

Báo cáo này tổng hợp kết quả kiểm tra 95 câu hỏi dành cho chatbot StudentHub UET. Mỗi câu được gửi đến chatbot qua API thực tế, sau đó câu trả lời được đọc và đối chiếu với tài liệu trong kho tri thức.

Dữ liệu sử dụng để tổng hợp gồm:

- Bộ câu hỏi: [cases.json](./q95-evaluation/cases.json)
- Các câu trả lời thực tế, nguồn truy xuất và các lần thử: [final-attempts.jsonl](./q95-evaluation/final-attempts.jsonl)
- Đánh giá thủ công câu 1–35: [review-01-35.json](./q95-evaluation/review-01-35.json)
- Đánh giá thủ công câu 36–66: [review-36-66.json](./q95-evaluation/review-36-66.json)
- Đánh giá thủ công câu 67–95: [review-67-95.json](./q95-evaluation/review-67-95.json)
- Bảng điểm dạng CSV: [q95-metric-scores.csv](./q95-metric-scores.csv)

Kết quả cuối gồm:

- **79 câu** được trả lời đầy đủ theo tài liệu đã đối chiếu.
- **13 câu** trả lời đúng phần có bằng chứng và nêu rõ phần tài liệu còn thiếu hoặc mâu thuẫn.
- **3 câu** ngoài phạm vi được xử lý phù hợp: Q50, Q94 và Q95.
- Không còn câu bị xếp loại sai nội dung hoặc thất bại kỹ thuật trong kết quả cuối đã lưu.

## 2. Quy tắc tính điểm tổng hợp

Điểm chất lượng tổng hợp sử dụng quy tắc sau:

| Trạng thái câu trả lời | Điểm mỗi câu |
|---|---:|
| Trả lời đầy đủ, đúng nguồn | 1,0 |
| Ngoài phạm vi và được xử lý đúng | 1,0 |
| Trả lời đúng phần có nguồn nhưng chưa thể trả lời đầy đủ | 0,5 |
| Sai nội dung hoặc lỗi dịch vụ | 0 |

Công thức:

```text
Điểm tổng hợp = (79 + 3 + 13 × 0,5) / 95 × 100
               = 88,5 / 95 × 100
               = 93,16/100
```

Việc cho câu giới hạn nguồn 0,5 điểm là quy ước của báo cáo này. Nó ghi nhận chatbot không bịa thông tin nhưng cũng không coi câu đó là đã được trả lời đầy đủ.

## 3. Bảng điểm metric

| Metric | Kết quả | Điểm | Ý nghĩa |
|---|---:|---:|---|
| **Overall Weighted Quality** | 88,5/95 | **93,16/100** | Điểm tổng hợp có tính nửa điểm cho 13 câu giới hạn nguồn. |
| **Full-answer Completeness** | 82/95 | **86,32/100** | 79 câu đầy đủ và 3 câu ngoài phạm vi được xử lý trọn vẹn. |
| **Retrieval/Evidence Coverage** | 79/92 | **85,87/100** | Trong 92 câu thuộc phạm vi, 79 câu có đủ bằng chứng để trả lời đầy đủ. |
| **Source-safe Handling** | 95/95 | **100/100 quan sát được** | Câu trả lời cuối bám nguồn, nói rõ giới hạn hoặc từ chối phù hợp. |
| **Answer Relevance** | 95/95 | **100/100 theo nhãn thủ công** | Câu trả lời cuối xử lý đúng vấn đề được hỏi hoặc đúng hướng ngoài phạm vi. |
| **Missing-information Handling** | 13/13 | **100/100** | Toàn bộ câu thiếu hoặc mâu thuẫn dữ liệu đều nêu giới hạn thay vì suy đoán. |
| **Out-of-scope Handling** | 3/3 | **100/100** | Q50, Q94 và Q95 không bị chatbot tự dựng câu trả lời. |
| **Technical Reliability** | 95/95 | **100/100 ở kết quả cuối** | Không còn lỗi HTTP, stream, quota hoặc transport trong kết quả cuối được chọn. |
| **Latency under 15 seconds** | 95/95 | **100/100 ở lượt đầu** | Thời gian lớn nhất của lượt đầu là 12,23 giây. |

## 4. Giải thích từng metric

### 4.1. Overall Weighted Quality — 93,16/100

Đây là chỉ số tổng hợp phù hợp để trình bày nhanh chất lượng chung của bộ kiểm thử. Chỉ số không đánh đồng câu trả lời có giới hạn nguồn với câu sai hoàn toàn: câu có giới hạn được nhận 0,5 điểm vì bot đã trả đúng phần có căn cứ và không bịa phần còn thiếu.

Chỉ số này do dự án tự định nghĩa, không phải metric mặc định của RAGAS.

### 4.2. Full-answer Completeness — 86,32/100

Metric đo tỷ lệ câu được xử lý trọn vẹn:

```text
(79 câu đầy đủ + 3 câu ngoài phạm vi xử lý đúng) / 95 × 100
= 86,32%
```

13 câu giới hạn nguồn không được tính là đầy đủ. Nguyên nhân là kho tài liệu chưa có đủ thông tin, có dữ liệu phụ thuộc ngành/khóa/cá nhân hoặc tồn tại hai nguồn chưa thống nhất.

### 4.3. Retrieval/Evidence Coverage — 85,87/100

Ba câu ngoài phạm vi được loại khỏi mẫu số. Trong 92 câu còn lại, 79 câu có đủ bằng chứng để chatbot trả lời hoàn chỉnh:

```text
79 / 92 × 100 = 85,87%
```

Metric này phản ánh độ bao phủ của kho tri thức và quá trình truy xuất. Nó không chỉ đo chất lượng thuật toán tìm kiếm, vì một số trường hợp thất bại do thông tin thực sự chưa tồn tại trong tài liệu.

### 4.4. Source-safe Handling — 100/100 quan sát được

Tất cả kết quả cuối đều thuộc một trong ba nhóm:

1. Trả lời có căn cứ từ tài liệu.
2. Trả đúng phần có bằng chứng và nói rõ giới hạn.
3. Từ chối hoặc yêu cầu thêm thông tin khi câu hỏi nằm ngoài phạm vi.

Con số này là **proxy thủ công cho Faithfulness**. Nó không phải điểm Faithfulness 1,0 được tạo bởi RAGAS hoặc một LLM judge độc lập. Vì vậy, khi viết báo cáo nên dùng cụm “tỷ lệ xử lý an toàn theo nguồn trong mẫu kiểm thử” thay cho “Faithfulness tuyệt đối”.

### 4.5. Answer Relevance — 100/100 theo nhãn thủ công

Đánh giá kiểm tra câu trả lời có đi đúng vào nội dung được hỏi, đúng ngành/chương trình và không thay câu hỏi bằng một chủ đề khác hay không. Các câu ngoài phạm vi đạt khi chatbot từ chối đúng hoặc yêu cầu dữ liệu cần thiết.

Đây cũng là proxy dựa trên đánh giá thủ công. Muốn có Answer Relevancy theo RAGAS cần chạy thêm LLM judge trên từng câu.

### 4.6. Xử lý thiếu thông tin — 100/100

Cả 13 câu có giới hạn tài liệu đều được chatbot nêu rõ phạm vi có thể kết luận. Metric này đánh giá hành vi an toàn, không khẳng định rằng 13 câu đã có đáp án hoàn chỉnh.

Ví dụ hành vi phù hợp:

- Không tự đặt mức phí khi tài liệu chưa xác nhận đúng loại phí.
- Không áp điều kiện của ngành này cho ngành khác.
- Không chọn tùy tiện một mốc thời hạn khi hai nguồn đang khác nhau.
- Yêu cầu thông tin ngành, khóa hoặc hồ sơ cá nhân khi kết luận phụ thuộc dữ liệu đó.

### 4.7. Xử lý ngoài phạm vi — 100/100

Q50, Q94 và Q95 được xác định trước là ngoài phạm vi kho tri thức. Chatbot đạt khi không tự dựng thông tin và phản hồi theo hướng từ chối hoặc yêu cầu nguồn/dữ kiện phù hợp.

### 4.8. Technical Reliability — 100/100 ở kết quả cuối

95 câu đều có kết quả cuối không bị lỗi HTTP, stream, quota hoặc transport. Đây là tỷ lệ của các kết quả cuối được lưu sau khi đã chạy lại những lượt gặp sự cố.

Metric này không có nghĩa dịch vụ sẽ luôn đạt 100%. Trong lịch sử kiểm thử từng xuất hiện quota, timeout và lỗi kết nối khi dịch vụ khởi động; các lỗi đó đã được giữ trong dữ liệu lần thử nhưng không còn ở kết quả cuối của từng câu.

### 4.9. Latency

Số liệu của lượt chạy đầu:

| Thống kê | Thời gian |
|---|---:|
| Trung bình | **6,07 giây** |
| Trung vị | **6,22 giây** |
| Chậm nhất | **12,23 giây** |
| Tỷ lệ dưới 15 giây | **95/95 — 100%** |

Mốc 15 giây là ngưỡng báo cáo tự chọn, không phải SLA chính thức của Gemini hay StudentHub.

## 5. So sánh trước và sau sửa

Lượt đánh giá ban đầu có:

- 44 câu đạt.
- 43 câu chưa đầy đủ.
- 5 câu không đạt.
- 3 câu ngoài phạm vi được xử lý đúng.

Áp dụng cùng quy tắc chấm:

```text
Điểm ban đầu = (44 + 3 + 43 × 0,5) / 95 × 100
              = 72,11/100

Điểm sau sửa = 93,16/100

Mức tăng      = 21,05 điểm phần trăm
```

Tỷ lệ xử lý hoàn chỉnh tăng từ:

```text
(44 + 3) / 95 = 49,47%

thành

(79 + 3) / 95 = 86,32%
```

## 6. Giới hạn của kết quả

- Đây là kết quả quan sát trên 95 câu cụ thể, không bảo đảm mọi cách diễn đạt khác đều cho kết quả giống nhau.
- Phần lớn câu được kiểm tra độc lập với lịch sử hội thoại rỗng; khả năng hội thoại nhiều lượt được kiểm tra ở bộ test khác.
- Các điểm Source-safe Handling và Answer Relevance là đánh giá thủ công, chưa phải kết quả RAGAS.
- Chưa có đáp án chuẩn chi tiết cho toàn bộ 95 câu, nên chưa thể tính Answer Correctness và Context Recall theo chuẩn tự động một cách đáng tin cậy.
- Điểm tổng hợp 93,16 sử dụng trọng số do báo cáo quy định. Khi so sánh với hệ thống khác phải dùng cùng cách chấm.

## 7. Kết luận dùng cho báo cáo

Có thể trình bày ngắn gọn như sau:

> Chatbot đạt điểm chất lượng tổng hợp **93,16/100** trên bộ 95 câu hỏi. Tỷ lệ xử lý hoàn chỉnh là **86,32%**, độ bao phủ bằng chứng đối với câu hỏi trong phạm vi là **85,87%**, và thời gian phản hồi trung bình ở lượt đo là **6,07 giây**. Các câu chưa thể trả lời đầy đủ đều được giới hạn theo tài liệu thay vì tự suy đoán. Faithfulness và Answer Relevance hiện được đánh giá thủ công; chưa phải điểm RAGAS tự động.
