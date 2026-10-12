# Phân tích lỗi Phase A

Nhóm: Dangcaps

Người phụ trách: Đỗ Ngọc Phi — 2A202602531 (m1/m4, Tasks 1–4). Báo cáo soạn từ
artifact live bởi Nguyễn Hải Nam — 2A202602476 (người chạy batch A).

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T17:00:48.875961+00:00 (UTC).
Generation mode/fallback và điều kiện chạy: cả 50 answers có `generation_mode=llm`,
không có extractive fallback. Pipeline thật: m1 hierarchical chunking (108 child
chunks; hai PDF scan BCTC.pdf và Nghị định 13 không trích được text nên bị bỏ qua,
không xóa khỏi corpus) → m5 enrichment (gpt-6-luna) → m2 BM25 + BGE-M3 dense trên
Qdrant v1.9.7 (RRF, top 20) → m3 CrossEncoder bge-reranker-v2-m3 (top 3) → generation.
Models generation/evaluator: generation = gpt-6-luna; evaluator = gpt-4o-mini, text-embedding-3-small
(lấy từ `metadata.evaluator_models` m4 trả về trong chính lượt chạy). Evaluator giữ
gpt-4o-mini vì RAGAS 0.1.22 ép temperature=1e-8, gpt-6-luna từ chối giá trị này và
mọi metric thành NaN khi thử.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9233 | 0.5492 | 0.8583 |
| answer_relevancy | 0.5079 | 0.3633 | 0.4940 |
| context_precision | 0.9417 | 0.9208 | 0.9583 |
| context_recall | 0.8333 | 0.7792 | 0.6167 |
| avg_score | 0.8016 | 0.6531 | 0.7318 |

Trung bình toàn bộ 50 câu: faithfulness 0.7607, avg_score 0.7282.

## Bottom 10 và nguyên nhân

Bảng giữ nguyên diagnosis/suggested_fix do Task 3 sinh ra (exporter không tính lại).

| Rank | ID | Question | Distribution | avg_score | worst_metric | Diagnosis | Suggested fix |
|---|---|---|---|---|---|---|---|
| 1 | 39 | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | multi_hop | 0.3714 | context_precision | Too many irrelevant chunks (context_precision=0.00); reference phân biệt phiên bản chính sách — rủi ro dùng bản cũ đã bị thay thế; câu multi-hop cần kết hợp nhiều tài liệu; top-k sau rerank có thể thiếu một nguồn | Add reranking or metadata filter; gắn metadata phiên bản/ngày hiệu lực khi chunking, ưu tiên bản hiện hành khi rerank và yêu cầu answer nêu phiên bản áp dụng (không xóa tài liệu cũ); tăng RERANK_TOP_K hoặc trả parent chunk cho câu cần nhiều nguồn |
| 2 | 35 | Nhân viên Junior P1 có lương cơ bản 12 triệu vừa vào thử việc: nhận lương bao nhiêu và phụ cấp gì tháng đầu tiên? | multi_hop | 0.3958 | answer_relevancy | Answer doesn't match question (answer_relevancy=0.00); answer trả 'không tìm thấy' — context lấy về không chứa thông tin cần | Improve prompt template; kiểm tra retrieval cho từ khóa của câu hỏi (BM25/dense, tăng top_k) trước khi sửa prompt |
| 3 | 7 | Nghỉ phép không lương 20 ngày cần ai phê duyệt? | factual | 0.4069 | faithfulness | LLM hallucinating (faithfulness=0.00) | Tighten system prompt, lower temperature |
| 4 | 22 | Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT? | multi_hop | 0.4167 | answer_relevancy | Answer doesn't match question (answer_relevancy=0.00) | Improve prompt template |
| 5 | 33 | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | multi_hop | 0.4583 | answer_relevancy | Answer doesn't match question (answer_relevancy=0.00); answer trả 'không tìm thấy' — context lấy về không chứa thông tin cần; reference phân biệt phiên bản chính sách — rủi ro dùng bản cũ đã bị thay thế | Improve prompt template; kiểm tra retrieval cho từ khóa của câu hỏi (BM25/dense, tăng top_k) trước khi sửa prompt; gắn metadata phiên bản/ngày hiệu lực khi chunking, ưu tiên bản hiện hành khi rerank và yêu cầu answer nêu phiên bản áp dụng (không xóa tài liệu cũ) |
| 6 | 44 | Bao lâu phải đổi mật khẩu một lần? | adversarial | 0.4792 | answer_relevancy | Answer doesn't match question (answer_relevancy=0.00); answer trả 'không tìm thấy' — context lấy về không chứa thông tin cần; reference phân biệt phiên bản chính sách — rủi ro dùng bản cũ đã bị thay thế | Improve prompt template; kiểm tra retrieval cho từ khóa của câu hỏi (BM25/dense, tăng top_k) trước khi sửa prompt; gắn metadata phiên bản/ngày hiệu lực khi chunking, ưu tiên bản hiện hành khi rerank và yêu cầu answer nêu phiên bản áp dụng (không xóa tài liệu cũ) |
| 7 | 21 | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | multi_hop | 0.5417 | answer_relevancy | Answer doesn't match question (answer_relevancy=0.00); answer trả 'không tìm thấy' — context lấy về không chứa thông tin cần; reference phân biệt phiên bản chính sách — rủi ro dùng bản cũ đã bị thay thế | Improve prompt template; kiểm tra retrieval cho từ khóa của câu hỏi (BM25/dense, tăng top_k) trước khi sửa prompt; gắn metadata phiên bản/ngày hiệu lực khi chunking, ưu tiên bản hiện hành khi rerank và yêu cầu answer nêu phiên bản áp dụng (không xóa tài liệu cũ) |
| 8 | 24 | Nhân viên tạm ứng 15 triệu, sau 20 ngày mới thanh toán. Bị phạt bao nhiêu? | multi_hop | 0.6057 | faithfulness | LLM hallucinating (faithfulness=0.00) | Tighten system prompt, lower temperature |
| 9 | 27 | Nhân viên có thâm niên 7 năm theo v2024 được nghỉ bao nhiêu ngày phép? Nếu bị trừ thêm 4 ngày ốm không có giấy y tế thì còn lại bao nhiêu? | multi_hop | 0.6087 | faithfulness | LLM hallucinating (faithfulness=0.00); reference phân biệt phiên bản chính sách — rủi ro dùng bản cũ đã bị thay thế | Tighten system prompt, lower temperature; gắn metadata phiên bản/ngày hiệu lực khi chunking, ưu tiên bản hiện hành khi rerank và yêu cầu answer nêu phiên bản áp dụng (không xóa tài liệu cũ) |
| 10 | 34 | Nhân viên tạm ứng 4 triệu và một nhân viên khác tạm ứng 7 triệu: quy trình phê duyệt khác nhau thế nào? | multi_hop | 0.6114 | answer_relevancy | Answer doesn't match question (answer_relevancy=0.11) | Improve prompt template |

Đối chiếu answer/contexts/reference của từng câu cho thấy bốn nhóm nguyên nhân khác
nhau; worst_metric một mình không đủ để kết luận.

**1. Retrieval thiếu một vế của câu multi-hop (lỗi thật của pipeline).** Câu 35, 33,
22, 21 cần ghép hai tài liệu nhưng top 3 sau rerank chỉ chứa một vế. Câu 35 có
`thu_viec.md` và `bang_luong_2024.md` nhưng không có `phu_cap.md`, nên answer tính
đúng lương thử việc 10,2 triệu rồi nói "không tìm thấy thông tin về phụ cấp". Câu 33
lấy cả ba chunk từ hai file nghỉ phép, không có chunk phụ cấp. Câu 21 lấy ba chunk
nghỉ phép, thiếu khung lương Senior. Câu 22 có chunk thẩm quyền mua sắm nhưng không
có mốc 5–50 triệu. Model trả lời trung thực phần thiếu, nên faithfulness không bằng 0
nhưng context_recall 0.25–0.50 và answer_relevancy 0 (RAGAS coi câu trả lời
"không tìm thấy" là noncommittal).

**2. Bẫy phiên bản (version conflict).** Câu 39 so sánh mật khẩu v1.0 và v2.0: ba
contexts có cả hai phiên bản nhưng không chứa độ dài 12 ký tự của v2.0, chu kỳ đổi
và MFA của v1.0, nên context_precision và context_recall đều 0.00; answer nêu rõ
phần thiếu thay vì bịa. Câu 44 (adversarial) lấy được chu kỳ của cả v1 (90 ngày) và
v2 (120 ngày) nhưng model từ chối chọn bản hiện hành ("không tìm thấy thông tin xác
định phiên bản nào áp dụng"), vì chunk chu kỳ không mang dấu hiệu hiệu lực: dòng
context do m5 sinh cho chunk v2 ghi "không nêu trạng thái hiệu lực".

**3. Faithfulness = 0 cho answer có căn cứ (giới hạn của evaluator, không phải
hallucination).** Câu 7 trả lời "CEO phê duyệt" và context 1 ghi nguyên văn "Nghỉ từ
16-30 ngày: cần phê duyệt của Giám đốc điều hành (CEO)". Câu 24 và 27 (cùng câu 38
ngoài bottom 10) là phép tính suy ra trực tiếp từ số liệu trong contexts
(2% × 15.000.000 × 5/30 = 50.000; 15 + 2 − 4 = 13; 3 × 200 USD = 600 USD) và khớp
reference, context_recall = 1.00. Evaluator gpt-4o-mini không xác minh được các
statement dạng phép tính hoặc tiếng Việt diễn đạt lại. Diagnosis "LLM hallucinating"
của Task 3 cho ba câu này là sai nguyên nhân.

**4. Answer relevancy thấp có hệ thống.** answer_relevancy là worst metric của
33/50 câu, kể cả câu đúng và ngắn (factual mean 0.5079).
Chín answer có chứa "không tìm thấy/không nêu" có mean 0.203, so với 0.501 ở phần
còn lại. Metric sinh câu hỏi ngược từ answer rồi so embedding với câu hỏi gốc, nên
answer tiếng Việt ngắn hoặc có phần thừa nhận thiếu thông tin bị điểm thấp dù đúng.

## Matrix và nhóm yếu nhất

Matrix đếm mọi câu theo metric thấp nhất của câu đó, không coi mọi câu là failure.
Tổng cột 20/20/10 chỉ là kích thước nhóm.

| worst_metric | factual | multi_hop | adversarial | Tổng |
|---|---|---|---|---|
| faithfulness | 2 | 7 | 1 | 10 |
| answer_relevancy | 15 | 12 | 6 | 33 |
| context_precision | 0 | 1 | 0 | 1 |
| context_recall | 3 | 0 | 3 | 6 |

Nhóm yếu theo mean thấp nhất: multi_hop; mean: 0.6531
(factual 0.8016, adversarial 0.7318).
Worst metric xuất hiện nhiều nhất: answer_relevancy; số câu: 33.

multi_hop yếu nhất vì faithfulness thấp nhất (0.5492) và
answer_relevancy thấp nhất (0.3633). Faithfulness thấp
đến từ hai nguồn đã tách ở trên: thiếu một vế retrieval (nhóm 1) và evaluator không
chấm được câu suy luận số (nhóm 3). Không dùng tổng 20/20/10 để chọn nhóm yếu.

Đề xuất sửa và cách đo lại:

1. Tăng `RERANK_TOP_K` từ 3 lên 5 cho câu có nhiều vế, hoặc tách câu hỏi thành
   sub-query rồi hợp nhất contexts; chạy lại setup và Phase A, kỳ vọng context_recall
   multi_hop tăng từ 0.7792 và số answer "không tìm thấy"
   giảm từ 9.
2. Ghi `version`, `effective_date`, `superseded_by` vào metadata ở m1 (đọc header
   tài liệu), lọc hoặc hạ hạng chunk của bản đã bị thay thế khi rerank, và thêm quy
   tắc "ưu tiên bản hiện hành" vào system prompt; đo lại câu 39 và 44.
3. Không sửa prompt theo diagnosis "hallucinating" của câu 7, 24, 27: bổ sung kiểm
   tra bằng judge có reference hoặc người duyệt mẫu cho các câu có phép tính trước
   khi kết luận faithfulness.
4. Theo dõi answer_relevancy cùng tỷ lệ answer "không tìm thấy" để phân biệt
   retrieval thiếu với answer lạc đề.

## Bẫy adversarial và giới hạn

Adversarial mean 0.7318 thấp hơn factual 0.8016 nhưng
cao hơn multi_hop. Đọc từng answer: 9/10 câu adversarial xử lý đúng bẫy về nội dung.
Version conflict: câu 41 (15 ngày v2024, không dùng 12 ngày v2023), 42 (mốc 3 năm),
43 (12 ký tự v2.0), 45 (MFA bắt buộc theo v2.0), 49 (nêu v2023 là cũ và v2024 đang
hiệu lực). Negation: câu 46, 47, 48 trả lời "Không" đúng. Policy contradiction: câu
50 trả lời không được dùng NordVPN. Câu sai duy nhất là 44, nằm trong bottom 10 với
avg 0.4792. Phần điểm thấp còn lại của adversarial chủ yếu do answer_relevancy
(mean 0.4940) và context_recall
(0.6167: reference nhắc cả phiên bản cũ lẫn mới,
top 3 thường chỉ có một bản), không phải do answer sai bẫy.

Điểm adversarial thấp hơn factual chỉ cho thấy nhóm này khó hơn, không tự chứng minh
pipeline nhận ra version conflict; kết luận 9/10 ở trên dựa trên đọc answer so với
reference, không dựa trên metric. Giới hạn: chỉ 50 câu (10 adversarial), một lượt
chạy, evaluator gpt-4o-mini cho điểm nhiễu với tiếng Việt và câu có phép tính, chưa
có nhãn người cho Phase A; generation dùng gpt-6-luna với temperature mặc định nên
chạy lại có thể khác answer.
