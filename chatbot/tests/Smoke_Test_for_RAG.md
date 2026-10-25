# BỘ DỮ LIỆU ĐÁNH GIÁ VÀ KIỂM THỬ ĐỘ CHÍNH XÁC CHATBOT AI (BENCHMARK TEST SUITE)

Tài liệu này chứa 20 ca kiểm thử (Test Cases) thực tế, đại diện cho các kịch bản hỏi đáp phổ biến nhất của sinh viên Trường Đại học Công nghệ (UET). Bộ câu hỏi này dùng làm căn cứ chuẩn (Ground Truth) để đánh giá độ chính xác truy xuất (Retrieval Accuracy) và chất lượng sinh câu trả lời (Answer Quality) của mô hình RAG tích hợp Gemini.

---

## BẢNG TỔNG HỢP 20 TEST CASES CHUẨN

| Mã TC | Phân hệ nghiệp vụ | Câu hỏi của sinh viên | Nguồn dữ liệu đối chiếu |
| :---: | :--- | :--- | :--- |
| **TC-01** | Học bổng & ĐRL | Điểm học bổng & Nguyên tắc lấy mức thấp hơn | `Hoc_bong_va_diem_ren_luyen.md` |
| **TC-02** | Học bổng & ĐRL | Khối lượng tín chỉ tối thiểu để xét HB | `Hoc_bong_va_diem_ren_luyen.md` |
| **TC-03** | Học bổng & ĐRL | Điểm cơ sở và quy tắc làm tròn ĐRL | `Hoc_bong_va_diem_ren_luyen.md` |
| **TC-04** | Học bổng & ĐRL | Mức khống chế ĐRL khi bị kỷ luật | `Hoc_bong_va_diem_ren_luyen.md` |
| **TC-05** | Thủ tục hành chính | Thời gian và địa điểm nhận bảng điểm | `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` |
| **TC-06** | Thủ tục hành chính | Thời hạn gửi đơn phúc khảo bài thi | `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` |
| **TC-07** | Thủ tục hành chính | Thời hạn và hồ sơ xin hoãn thi | `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` |
| **TC-08** | Thủ tục hành chính | Hồ sơ xin nghỉ học tạm thời (bảo lưu) | `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` |
| **TC-09** | Khen thưởng & Kỷ luật | Mức phạt điểm thi khi bị cảnh cáo phòng thi | `Khen_thuong_ky_luat.md` & `Quy_che_dao_tao.md` |
| **TC-10** | Khen thưởng & Kỷ luật | Thời hạn xóa án kỷ luật Khiển trách / Cảnh cáo | `Khen_thuong_ky_luat.md` |
| **TC-11** | Khen thưởng & Kỷ luật | Tiêu chuẩn đạt danh hiệu "Sinh viên Giỏi" cuối năm | `Khen_thuong_ky_luat.md` |
| **TC-12** | Khen thưởng & Kỷ luật | Chế tài xử lý hành vi thi hộ / nhờ thi hộ | `Khen_thuong_ky_luat.md` & `Quy_che_dao_tao.md` |
| **TC-13** | Quy chế đào tạo | Điều kiện cảnh báo học vụ theo GPA tích lũy | `Quy_che_dao_tao.md` |
| **TC-14** | Quy chế đào tạo | Các trường hợp bị buộc thôi học | `Quy_che_dao_tao.md` |
| **TC-15** | Quy chế đào tạo | Quy định học cải thiện điểm D và D+ | `Quy_che_dao_tao.md` |
| **TC-16** | Quy chế đào tạo | Số tín chỉ đăng ký tối thiểu/tối đa kỳ chính | `Quy_che_dao_tao.md` |
| **TC-17** | Học phí & Chính sách | Giới hạn số lần bấm tạo lệnh thanh toán QR | `Quy_dinh_ve_hoc_phi.md` |
| **TC-18** | Học phí & Chính sách | Danh sách 16 dân tộc thiểu số miễn 100% học phí | `Quy_dinh_ve_hoc_phi.md` |
| **TC-19** | Liên hệ & Hỗ trợ | Địa chỉ và hotline Phòng Công tác Sinh viên | `Thong_tin_lien_he_voi_nha_truong.md` |
| **TC-20** | Liên hệ & Hỗ trợ | Kênh liên hệ Phòng Đào tạo UET | `Thong_tin_lien_he_voi_nha_truong.md` |

---

## CHI TIẾT NỘI DUNG 20 TEST CASES

### TC-01: Nguyên tắc xét học bổng khi GPA và ĐRL không cùng mức
* **Câu hỏi kiểm thử:** *"Kỳ này GPA của em là 3.65 nhưng Điểm rèn luyện chỉ được 78 điểm thì em có được học bổng Xuất sắc không, hay được loại gì?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Không được học bổng Xuất sắc. 
  * Sinh viên sẽ được xét học bổng **loại Khá**.
  * *Lý do:* Theo quy định tại Quyết định 1931/QĐ-ĐHCN, mức học bổng được xét dựa trên **mức thấp hơn** giữa kết quả học tập và kết quả rèn luyện. GPA 3.65 đạt mức Xuất sắc ($\ge 3.60$), nhưng ĐRL 78 điểm chỉ đạt mức Khá (65 – 79 điểm), do đó mức xét cuối cùng là loại Khá.
* **Tệp dữ liệu nguồn:** `Hoc_bong_va_diem_ren_luyen.md` (Phần I, Mục 2 & Mục 4).
* **Từ khóa bắt buộc:** `loại Khá`, `nguyên tắc lấy mức thấp hơn`, `78 điểm đạt loại Khá`.

---

### TC-02: Số tín chỉ tối thiểu để đủ điều kiện xét học bổng KKHT
* **Câu hỏi kiểm thử:** *"Kỳ này mình đăng ký và tích lũy được 14 tín chỉ, GPA 3.8 và ĐRL 92 thì có được xét học bổng khuyến khích học tập không?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Không được xét học bổng khuyến khích học tập.
  * *Lý do:* Quy định nêu rõ tại học kỳ xét học bổng, sinh viên bắt buộc phải hoàn thành **ít nhất 15 tín chỉ** trong khung chương trình đào tạo. Dù GPA và ĐRL đều đạt loại Xuất sắc nhưng thiếu điều kiện khối lượng tín chỉ tối thiểu (14 < 15).
* **Tệp dữ liệu nguồn:** `Hoc_bong_va_diem_ren_luyen.md` (Phần I, Mục 3).
* **Từ khóa bắt buộc:** `ít nhất 15 tín chỉ`, `không đủ điều kiện`.

---

### TC-03: Điểm rèn luyện cơ sở và nguyên tắc làm tròn
* **Câu hỏi kiểm thử:** *"Đầu kỳ điểm rèn luyện mặc định của sinh viên là bao nhiêu, và ĐRL có lấy số thập phân không?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Điểm rèn luyện cơ sở mặc định là **70 điểm** (áp dụng cho sinh viên không vi phạm quy chế), sau đó cộng hoặc trừ theo minh chứng hoạt động.
  * Điểm rèn luyện **không tính điểm lẻ** (làm tròn thành số nguyên).
* **Tệp dữ liệu nguồn:** `Hoc_bong_va_diem_ren_luyen.md` (Phần III, Mục 1).
* **Từ khóa bắt buộc:** `70 điểm`, `không tính điểm lẻ` / `làm tròn thành số nguyên`.

---

### TC-04: Mức trần ĐRL khi bị kỷ luật Khiển trách
* **Câu hỏi kiểm thử:** *"Sinh viên bị kỷ luật khiển trách thì điểm rèn luyện cao nhất trong kỳ có thể đạt được là loại gì?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Sinh viên bị kỷ luật Khiển trách thì kết quả rèn luyện trong kỳ bị khống chế **tối đa đạt loại Khá** (từ 65 đến dưới 80 điểm, không được vượt quá loại Khá).
* **Tệp dữ liệu nguồn:** `Hoc_bong_va_diem_ren_luyen.md` (Phần III, Mục 3) hoặc `Khen_thuong_ky_luat.md`.
* **Từ khóa bắt buộc:** `tối đa loại Khá`, `khiển trách`.

---

### TC-05: Địa điểm và lịch trả Bảng điểm sinh viên
* **Câu hỏi kiểm thử:** *"Mình xin cấp bảng điểm trên Student Hub thì bao giờ có và đến đâu để lấy?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Nhận kết quả sau **15h00 các ngày thứ Tư và thứ Sáu hàng tuần**.
  * Địa điểm nhận: **Phòng Công tác Sinh viên (Phòng 107 – Nhà G2)**.
* **Tệp dữ liệu nguồn:** `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` (Mục 2).
* **Từ khóa bắt buộc:** `sau 15h00`, `thứ Tư và thứ Sáu`, `Phòng 107 – G2`.

---

### TC-06: Thời hạn nộp yêu cầu phúc khảo bài thi
* **Câu hỏi kiểm thử:** *"Sau khi biết điểm thi kết thúc học phần, em có bao nhiêu ngày để làm đơn xin phúc khảo xem lại bài thi?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Sinh viên tạo yêu cầu phúc khảo trên cổng Student Hub trong vòng **05 ngày làm việc** tính từ ngày điểm thi được công bố chính thức.
* **Tệp dữ liệu nguồn:** `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` (Mục 4).
* **Từ khóa bắt buộc:** `05 ngày làm việc`, `tính từ ngày điểm thi được công bố`.

---

### TC-07: Quy định về thời hạn nộp đơn xin hoãn thi
* **Câu hỏi kiểm thử:** *"Nếu bị ốm đột xuất không thể đi thi kết thúc môn, em phải làm thủ tục hoãn thi trước bao lâu?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Sinh viên đăng nhập Student Hub tạo yêu cầu hoãn thi kèm bản mềm minh chứng hợp lệ **trước ngày thi ít nhất 3 ngày** (hoặc ngay sau khi thi đối với trường hợp cấp bách/bất khả kháng có xác nhận của cơ sở y tế).
* **Tệp dữ liệu nguồn:** `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` (Mục 3).
* **Từ khóa bắt buộc:** `trước ngày thi ít nhất 3 ngày`, `ngay sau khi thi`, `minh chứng`.

---

### TC-08: Hồ sơ và thủ tục xin nghỉ học tạm thời (bảo lưu)
* **Câu hỏi kiểm thử:** *"Muốn bảo lưu kết quả học tập để đi chữa bệnh thì cần chuẩn bị những giấy tờ gì và nhận quyết định ở đâu?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Hồ sơ gồm 4 loại giấy tờ:
    1. Đơn xin nghỉ học có thời hạn (có ý kiến phụ huynh và xác nhận của UBND xã/phường).
    2. Giấy xác nhận không nợ sách từ Thư viện ĐHQGHN (Nhà C1T).
    3. Giấy chỉ định điều trị của bác sĩ (bắt buộc phải có **dấu tròn** của cơ sở y tế).
    4. Biên lai/minh chứng hoàn thành nộp đủ học phí đến thời điểm xin nghỉ.
  * Địa điểm nhận kết quả: Sau **05 ngày làm việc** kể từ ngày hồ sơ được duyệt, nhận Quyết định tại **Phòng 107 – G2**.
* **Tệp dữ liệu nguồn:** `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` (Mục 10).
* **Từ khóa bắt buộc:** `Nhà C1T`, `dấu tròn`, `không nợ sách`, `05 ngày làm việc`, `Phòng 107 – G2`.

---

### TC-09: Mức trừ điểm thi khi bị kỷ luật Cảnh cáo phòng thi
* **Câu hỏi kiểm thử:** *"Sinh viên bị lập biên bản cảnh cáo trong phòng thi kết thúc môn thì bài thi bị trừ bao nhiêu % điểm?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Sinh viên bị kỷ luật cảnh cáo trong giờ thi học phần nào sẽ bị **trừ 50% số điểm** đạt được của bài thi học phần đó.
* **Tệp dữ liệu nguồn:** `Quy_che_dao_tao.md` (Điều 35, Khoản 4b) hoặc `Khen_thuong_ky_luat.md` (Phần III, Mục 9).
* **Từ khóa bắt buộc:** `trừ 50% số điểm`, `cảnh cáo`.

---

### TC-10: Thời hạn tự động xóa án kỷ luật sinh viên
* **Câu hỏi kiểm thử:** *"Bị trường kỷ luật Khiển trách hoặc Cảnh cáo thì sau bao lâu sẽ hết hiệu lực?"*
* **Đáp án chuẩn (Ground Truth):** 
  * **Kỷ luật Khiển trách:** Chấm dứt hiệu lực sau **03 tháng** kể từ ngày ký quyết định (nếu không tái phạm).
  * **Kỷ luật Cảnh cáo:** Chấm dứt hiệu lực sau **06 tháng** kể từ ngày ký quyết định (nếu không tái phạm).
* **Tệp dữ liệu nguồn:** `Khen_thuong_ky_luat.md` (Phần II, Mục 2).
* **Từ khóa bắt buộc:** `sau 03 tháng` (khiển trách), `sau 06 tháng` (cảnh cáo), `không tái phạm`.

---

### TC-11: Điều kiện xét danh hiệu cá nhân "Sinh viên Giỏi" cuối năm học
* **Câu hỏi kiểm thử:** *"Tiêu chuẩn để được nhận danh hiệu Sinh viên Giỏi vào cuối năm học là gì?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Điểm trung bình học tập năm học đạt loại Giỏi: $\text{GPA} \ge 3.20$.
  * Điểm rèn luyện cả năm đạt từ loại Tốt trở lên: $\text{ĐRL} \ge 80$ điểm.
  * **Điều kiện bắt buộc:** Không có học phần nào bị điểm F trong năm học; không bị kỷ luật từ mức khiển trách trở lên; không có môn nào điểm kết thúc học phần dưới 2.00.
* **Tệp dữ liệu nguồn:** `Khen_thuong_ky_luat.md` (Phần I, Mục 1).
* **Từ khóa bắt buộc:** `GPA $\ge 3.20$`, `ĐRL $\ge 80$` (loại Tốt), `không có môn nào bị điểm F`.

---

### TC-12: Chế tài đối với hành vi thi hộ hoặc nhờ người thi hộ
* **Câu hỏi kiểm thử:** *"Nếu nhờ người khác đi thi hộ hoặc đi thi hộ cho bạn thì bị kỷ luật thế nào?"*
* **Đáp án chuẩn (Ground Truth):** 
  * **Vi phạm lần thứ nhất:** Kỷ luật ở mức **Đình chỉ học tập 01 năm**.
  * **Vi phạm lần thứ hai:** Kỷ luật ở mức **Buộc thôi học** (xóa tên khỏi danh sách sinh viên).
* **Tệp dữ liệu nguồn:** `Quy_che_dao_tao.md` (Điều 35, Khoản 4d) hoặc `Khen_thuong_ky_luat.md` (Phần III, Mục 2).
* **Từ khóa bắt buộc:** `Đình chỉ học tập 1 năm` (lần 1), `Buộc thôi học` (lần 2).

---

### TC-13: Mức điểm xét cảnh báo học vụ của sinh viên năm 2
* **Câu hỏi kiểm thử:** *"Sinh viên năm thứ 2 có điểm CPA tích lũy dưới bao nhiêu thì bị rơi vào danh sách cảnh báo học tập?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Sinh viên năm thứ hai bị cảnh báo học vụ nếu điểm trung bình chung tích lũy (CPA) đạt **dưới 1.40**.
  * *(Các mốc tham chiếu khác: Năm 1 dưới 1.20; Năm 3 dưới 1.60; Năm 4 và các năm sau dưới 1.80).*
* **Tệp dữ liệu nguồn:** `Quy_che_dao_tao.md` (Điều 44, Khoản 1a).
* **Từ khóa bắt buộc:** `dưới 1.40`, `sinh viên năm thứ hai`.

---

### TC-14: Các trường hợp sinh viên bị buộc thôi học theo quy chế
* **Câu hỏi kiểm thử:** *"Những trường hợp nào sinh viên sẽ bị Nhà trường buộc thôi học?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Sinh viên bị buộc thôi học khi rơi vào một trong các trường hợp sau:
    1. Bị cảnh báo kết quả học tập vượt quá số lần quy định (quá 2 lần liên tiếp).
    2. Vượt quá thời gian tối đa được phép học của khóa học (quá 2 lần thời gian thiết kế chuẩn).
    3. Thi hộ hoặc nhờ thi hộ lần thứ hai; làm giả chứng chỉ ngoại ngữ; vi phạm pháp luật bị phạt tù giam.
    4. Không đăng ký học trong **02 học kỳ liên tiếp**.
    5. Hết thời hạn nghỉ học tạm thời nhưng không có đơn xin trở lại học tập.
* **Tệp dữ liệu nguồn:** `Quy_che_dao_tao.md` (Điều 44, Khoản 2).
* **Từ khóa bắt buộc:** `quá 2 lần liên tiếp`, `vượt quá thời gian tối đa`, `không đăng ký học 2 học kỳ liên tiếp`, `hết hạn nghỉ tạm thời`.

---

### TC-15: Quy định hủy điểm cũ khi học cải thiện điểm D/D+
* **Câu hỏi kiểm thử:** *"Em được điểm D môn Giải tích 1, nếu đăng ký học cải thiện thì điểm cũ có được giữ lại nếu điểm mới thấp hơn không?"*
* **Đáp án chuẩn (Ground Truth):** 
  * **Không được giữ lại điểm cũ.**
  * Theo quy định, khi việc đăng ký học lại để cải thiện điểm được chấp nhận, **điểm học phần cũ sẽ bị hủy bỏ** và được thay thế hoàn toàn bằng điểm của học phần học cải thiện.
* **Tệp dữ liệu nguồn:** `Quy_che_dao_tao.md` (Điều 21, Khoản 5).
* **Từ khóa bắt buộc:** `hủy bỏ`, `thay bằng điểm học phần để cải thiện`, `không giữ điểm cũ`.

---

### TC-16: Khối lượng tín chỉ đăng ký tối thiểu và tối đa trong học kỳ chính
* **Câu hỏi kiểm thử:** *"Trong một học kỳ chính sinh viên được đăng ký tối thiểu và tối đa bao nhiêu tín chỉ?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Khối lượng đăng ký tối thiểu không ít hơn **$2/3$ khối lượng trung bình một học kỳ** theo kế hoạch chuẩn (khoảng 10 – 12 tín chỉ tùy ngành).
  * Khối lượng tối đa không vượt quá **$3/2$ khối lượng trung bình một học kỳ** theo kế hoạch chuẩn (không quá 24 tín chỉ).
  * Quy định này không áp dụng cho học kỳ cuối khóa của sinh viên.
* **Tệp dữ liệu nguồn:** `Quy_che_dao_tao.md` (Điều 21, Khoản 1).
* **Từ khóa bắt buộc:** `2/3 khối lượng trung bình`, `3/2 khối lượng trung bình`.

---

### TC-17: Giới hạn tạo lệnh thanh toán học phí trên Student Hub
* **Câu hỏi kiểm thử:** *"Một ngày em được bấm tạo mã QR thanh toán học phí trên trang Student Hub tối đa bao nhiêu lần?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Mỗi ngày hệ thống Student Hub chỉ cho phép sinh viên ấn tạo lệnh thanh toán **tối đa 5 lần**. Sau khi quét mã thành công cần đợi trong giây lát để hệ thống cập nhật gạch nợ.
* **Tệp dữ liệu nguồn:** `Quy_dinh_ve_hoc_phi.md` (Mục II).
* **Từ khóa bắt buộc:** `tối đa 5 lần`, `mỗi ngày`.

---

### TC-18: Đối tượng 16 dân tộc thiểu số rất ít người được miễn 100% học phí
* **Câu hỏi kiểm thử:** *"Những dân tộc thiểu số rất ít người nào được nhà nước miễn 100% học phí tại UET?"*
* **Đáp án chuẩn (Ground Truth):** 
  * Gồm 16 dân tộc có dân số dưới 10.000 người theo Nghị định 57/2017/NĐ-CP: 
    * **Cống, Mảng, Pu Péo, Si La, Cờ Lao, Bố Y, La Ha, Ngái, Chứt, Ơ Đu, Brâu, Rơ Măm, Lô Lô, Lự, Pà Thèn, La Hủ**.
* **Tệp dữ liệu nguồn:** `Quy_dinh_ve_hoc_phi.md` (Mục IV, Khoản 1.5).
* **Từ khóa bắt buộc:** Liệt kê đúng các dân tộc (tối thiểu nhắc các nhóm: `Ơ Đu`, `Brâu`, `Rơ Măm`, `Pu Péo`, `Si La`).

---

### TC-19: Thông tin liên hệ đầy đủ của Phòng Công tác Sinh viên UET
* **Câu hỏi kiểm thử:** *"Cho mình xin số điện thoại, email và phòng làm việc của Phòng Công tác Sinh viên trường ĐH Công nghệ?"*
* **Đáp án chuẩn (Ground Truth):** 
  * **Số điện thoại:** `024 3754 8864`
  * **Email:** `ctsv_dhcn@vnu.edu.vn`
  * **Địa điểm làm việc:**
    * Bộ phận Một cửa (tiếp nhận giấy tờ, thẻ SV): **Phòng 107, Nhà G2**, 144 Xuân Thủy.
    * Văn phòng chuyên trách chính sách & học bổng: **Phòng 210, Nhà G2**, 144 Xuân Thủy.
* **Tệp dữ liệu nguồn:** `Thong_tin_lien_he_voi_nha_truong.md` (Mục 1).
* **Từ khóa bắt buộc:** `024 3754 8864`, `ctsv_dhcn@vnu.edu.vn`, `Phòng 107, Nhà G2`, `Phòng 210, Nhà G2`.

---

### TC-20: Đầu mối liên hệ của Phòng Đào tạo UET
* **Câu hỏi kiểm thử:** *"Mình bị lỗi đăng ký môn học và cần hỏi về lịch thi thì liên hệ Phòng Đào tạo qua số điện thoại nào và ở đâu?"*
* **Đáp án chuẩn (Ground Truth):** 
  * **Số điện thoại đào tạo đại học:** `024 3202 6858`
  * **Địa chỉ làm việc:** **Phòng 213, Nhà G2** (144 Xuân Thủy, Cầu Giấy, Hà Nội).
  * **Website chính thức:** `https://uet.vnu.edu.vn/phong-dao-tao/`
* **Tệp dữ liệu nguồn:** `Thong_tin_lien_he_voi_nha_truong.md` (Mục 2 & Mục 4).
* **Từ khóa bắt buộc:** `024 3202 6858`, `Phòng 213, Nhà G2`.