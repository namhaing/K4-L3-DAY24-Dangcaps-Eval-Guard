# Đánh giá LLM Judge Phase B

Nhóm: Dangcaps

Người phụ trách: Phạm Cường Quốc — 2A202602469 (Tasks 5–6: pairwise, swap) và
Nguyễn Hải Nam — 2A202602476 (Tasks 7–8: Cohen's κ, bias report; chạy batch B và
soạn báo cáo này).

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T17:02:08.608036+00:00 (UTC).
Models generation/judge: generation = gpt-6-luna (nguồn
candidate A); judge = gpt-6-luna cho cả pairwise judge và helper
`judge_binary`. gpt-6-luna chỉ nhận temperature mặc định nên judge không đặt
temperature=0; mỗi lượt gọi là một mẫu, không lấy trung bình nhiều mẫu.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ
fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge. Lượt 1 judge(A, B),
lượt 2 judge(B, A) cùng question/reference; winner và scores lượt 2 đã quy về A/B gốc.

| ID | Candidate A (pipeline) | Candidate B (supplied) | winner_pass1 | winner_pass2 | final_winner | position_consistent | Scores lượt 1 / lượt 2 | Reasoning lượt 1 |
|---|---|---|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ có lương 3 ngày làm việc khi kết hôn. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | tie | tie | tie | True | A=1.00, B=1.00 / A=1.00, B=1.00 | Cả hai câu trả lời đều nêu đúng nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn và trả lời đủ câu hỏi. |
| 5 | Đơn hàng 55 triệu VNĐ cần Tổng Giám đốc (CEO) phê duyệt. | Cần Giám đốc phòng ban phê duyệt. | A | A | A | True | A=1.00, B=0.00 / A=1.00, B=0.00 | A đúng chính sách: đơn hàng 55 triệu đồng vượt ngưỡng 50 triệu nên cần CEO phê duyệt. B nêu sai người phê duyệt. |
| 12 | Tối thiểu 1 tháng lương. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | A | A | A | True | A=1.00, B=0.80 / A=1.00, B=0.80 | A trả lời đúng mức thưởng tối thiểu và không khái quát áp dụng cho mọi nhân viên. B bỏ điều kiện nhân viên chính thức có từ 6 tháng trở lên nên kém chính xác hơn. |
| 21 | Nhân viên có 9 năm thâm niên được 18 ngày phép năm có lương (15 + 3). Khoảng lương không tìm thấy. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | B | B | B | True | A=0.50, B=1.00 / A=0.60, B=1.00 | B trả lời đầy đủ và khớp đáp án tham chiếu: 18 ngày phép và mức lương Senior 20–35 triệu đồng/tháng. A thiếu khoảng lương. |
| 41 | Nhân viên chính thức được 15 ngày phép năm có lương. Thâm niên có thể làm tăng số ngày; ví dụ, nhân viên có 9 năm thâm niên được 18 ngày. | Nhân viên được nghỉ 12 ngày phép năm. | A | A | A | True | A=1.00, B=0.00 / A=1.00, B=0.00 | A ưu tiên đúng chính sách hiện hành v2024: 15 ngày cơ bản, tăng 1 ngày mỗi 3 năm thâm niên; ví dụ 9 năm được 18 ngày. B nêu mức 12 ngày của chính sách v2023 đã bị thay thế. |

Position bias count/rate: 0/5 = 0.000.
Verbosity win rate: 0.500; decisive cases: 4
(a_wins_a_longer = 2, b_wins_b_longer = 0).

Không có cặp nào đổi winner khi hoán vị: cả năm cặp cho cùng kết luận ở hai lượt, và
scores hai lượt gần như trùng nhau (chỉ câu 21 lệch 0.1 điểm cho A). Reasoning lượt 2
viết theo nhãn vị trí của lượt đó (ví dụ câu 5 lượt 2 viết "B khớp chính sách" vì CEO
nằm ở vị trí B), nhưng sau khi quy đổi vẫn là cùng candidate A thắng.

Verbosity 0.5 là dấu hiệu thống kê, không phải bằng chứng bias. Hai case "answer dài
hơn thắng" là câu 5 và 41, và cả hai B đều sai theo reference: câu 5 B nói Giám đốc
phòng ban phê duyệt đơn 55 triệu (đúng là CEO), câu 41 B trả lời 12 ngày theo v2023 đã
hết hiệu lực (đúng là 15 ngày v2024). Ngược lại, hai case decisive còn lại là câu ngắn
hơn thắng: câu 12 A ngắn hơn ("Tối thiểu 1 tháng lương") thắng vì B khái quát cho mọi
nhân viên, và câu 21 B ngắn hơn thắng vì A thiếu khung lương Senior. Câu 1 tie vì hai
answer tương đương. Nội dung reasoning cho thấy judge quyết định theo độ chính xác so
với reference, nên mẫu này không cho thấy verbosity bias.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json;
không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference.
Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt. Runner tạo đủ 10
nhãn judge trước, sau đó mới đọc human_label để so sánh theo cùng thứ tự ids.

| question_id | model_answer gốc | Nhãn judge | Reasoning judge | human_label | Agree |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | Câu trả lời nêu đúng 3 ngày làm việc có lương khi kết hôn, đáp ứng ý chính của câu hỏi. Việc không trừ vào phép năm là thông tin bổ sung. | 1 | có |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | Thiết bị trị giá 55 triệu vượt 50 triệu nên cần Tổng Giám đốc (CEO) phê duyệt, không phải Giám đốc phòng ban. | 0 | có |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | Đúng mức thưởng tối thiểu 1 tháng lương cho nhóm nhân viên chính thức có từ 6 tháng trở lên được hỏi. | 1 | có |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | Đúng theo chính sách v2024: 18 ngày phép năm và mức lương Senior 20–35 triệu VNĐ/tháng. | 1 | có |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | Nghỉ sau 8 tháng là chưa đủ thời hạn cam kết 1 năm, nên phải hoàn trả 100% chi phí là 25 triệu đồng. | 1 | có |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | Thiếu Kế toán trưởng trong phê duyệt; khoản 8 triệu cần Trưởng phòng và Kế toán trưởng. Phí phạt theo reference là 80.000 VNĐ, không chỉ là 2%/tháng trên 8 triệu. | 0 | có |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | Phụ cấp tháng tổng cộng 1.500.000 VNĐ và phép năm là 19 ngày, đúng theo reference. | 1 | có |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | Câu trả lời dùng mức 12 ngày của chính sách v2023 đã bị thay thế; chính sách hiện hành v2024 quy định 15 ngày cơ bản, cộng 1 ngày mỗi 3 năm thâm niên. | 0 | có |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 0 | Trả lời đúng rằng nhân viên thử việc không được nghỉ phép năm, nhưng khi nói về nghỉ không lương thì bỏ sót điều kiện phải được trưởng phòng phê duyệt. | 1 | không |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | Reference cấm VPN cá nhân như NordVPN và yêu cầu dùng VPN WireGuard của công ty. Answer lại nói được dùng nếu kết nối an toàn, trái chính sách. | 0 | có |

Cohen’s κ: 0.8000.
Observed/chance agreement và diễn giải: đồng ý 9/10 câu nên p_o = 0.90. Judge
gán nhãn 1 cho 5/10 câu, người gán nhãn 1 cho 6/10 câu, nên
p_e = 0.5 × 0.6 + 0.5 × 0.4 = 0.50.
κ = (0.90 − 0.50) / (1 − 0.50) = 0.80, mức "substantial" theo
Landis–Koch và vượt ngưỡng 0.6. Tỷ lệ trùng 90% cao hơn κ vì một nửa mức trùng có thể
đạt do may rủi khi nhãn phân bố 6/4.

Case lệch duy nhất là câu 46: answer "không được nghỉ phép năm và phải xin nghỉ không
lương nếu cần", người gán 1 (đúng và đủ hành động thay thế), judge gán 0 vì answer bỏ
điều kiện "được trưởng phòng phê duyệt" có trong reference. Judge chặt hơn người ở chi
tiết điều kiện phụ; đây là khác biệt về mức độ "ý thiết yếu", không phải lỗi đảo phủ
định.

## Giới hạn và cách dùng judge

Mẫu rất nhỏ: 5 cặp pairwise và 10 nhãn nhị phân, nên một nhãn đổi có thể làm κ thay
đổi mạnh (nếu câu 46 khớp thì κ = 1.0; thêm một câu lệch thì κ còn khoảng 0.6). Chỉ
dùng một model judge (gpt-6-luna) và một lượt chạy với temperature mặc định, chưa đo độ
ổn định khi chạy lại. Position bias 0/5 chỉ áp dụng cho năm cặp có một candidate sai
rõ hoặc hai candidate tương đương; cặp khó hơn có thể lộ bias. Judge dùng reference
nên phụ thuộc chất lượng reference.

Cách dùng: judge phù hợp để sàng lọc và xếp hạng nhanh, luôn chạy hai thứ tự A/B và
giữ tie khi lệch. Không xem judge là đáp án tuyệt đối: case như câu 46 (điều kiện phụ)
cần người duyệt, và nên mở rộng bộ nhãn người lên vài chục câu, đo κ định kỳ khi đổi
model hoặc prompt judge.
