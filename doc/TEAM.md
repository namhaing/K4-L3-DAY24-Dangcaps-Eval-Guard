# Nhóm thực hiện K4 Track 3A

Tên nhóm: {{Tên nhóm}}

Repo chung: {{Link repo}}

Trưởng nhóm/người nộp: {{Họ tên và MSSV}}

Ngày lab/deadline áp dụng: {{Ngày giờ theo thông báo lớp}} — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 2 | Đỗ Ngọc Phi | 2A202602531 | Tích hợp m1 + m4 (evaluator_models); Phase A Tasks 1–4; failure_clusters.md; blueprint Monitoring | Nhánh phi-phase-a, PR #2; src/m1_chunking.py, src/m4_eval.py, src/phase_a_ragas.py |
| 3 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: {{Phiên bản thực tế}}.
Virtualenv/dependencies/imports: {{Lệnh và kết quả}}.
Models/Qdrant/50 answers đã chuẩn bị: {{Bằng chứng và giới hạn/fallback}}.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### {{HoVaTen}}-{{MSSV}}

- Phần được giao và phần thực tế đã làm: {{Nhiệm vụ, file/hàm, mục đích}}.
- Bằng chứng: {{Commit/PR và artifacts/reports liên quan}}.
- Cách kiểm tra: {{Unit mock hoặc live experiment, lệnh và kết quả}}.
- Điều đã học: {{Khái niệm và cách thể hiện trong bài}}.
- Giới hạn/cách xử lý: {{Vấn đề và kiểm chứng}}.
- Nguồn/AI hỗ trợ nếu có: {{Công cụ, phạm vi, cách tự kiểm chứng}}.

### DoNgocPhi-2A202602531

- Phần được giao và phần thực tế đã làm: tích hợp m1_chunking và m4_eval từ bài Day 18 của Phi; sửa m4 truyền evaluator tường minh và trả `metadata.evaluator_models`, không thay NaN/thiếu bằng điểm giả; implement Phase A Task 1 `group_by_distribution`, Task 2 `run_ragas_50q`, Task 3 `bottom_10` (diagnosis suy ra từ dữ liệu từng câu: bẫy phiên bản, phủ định, "không tìm thấy", multi-hop), Task 4 `cluster_analysis` (nhóm yếu theo mean thấp nhất).
- Bằng chứng: PR #2 nhánh phi-phase-a; commit 68f9c69 (m1), 4d666f4 (m4), 2f0c727 (Task 1), bd7d626 (Task 2), ee5b5fa (Task 3), 8f35eb2 (Task 4). Chưa có artifacts/ragas_50q.json live; failure_clusters.md và blueprint Monitoring điền sau khi Nam chạy batch A.
- Cách kiểm tra: `python -m pytest tests/test_phase_a.py -q` đạt 6 tests (mock m4, offline); tự thử NaN/thiếu dòng/thiếu evaluator_models đều raise; chạy thử end-to-end bằng điểm giả lập trong bộ nhớ qua `validate_phase_a` của checker đạt. m4 kiểm tra offline trên ragas 0.1.22 + langchain-openai 0.1.25 bằng hàm evaluate giả. Đây là mock/offline, không phải bằng chứng chạy API.
- Môi trường: macOS, Python 3.11 (`.venv-tests` cài từ requirements-test.lock.txt); venv riêng cho stack RAGAS pin theo constraints-core.
- Điều đã học: bốn metric RAGAS tách lỗi retrieval (context_precision/recall) khỏi lỗi generation (faithfulness/answer_relevancy); matrix worst_metric chỉ mô tả phân bố, nhóm yếu phải chọn bằng mean chứ không bằng số câu; provenance model evaluator phải lấy từ chính lượt chạy, không suy từ model judge.
- Giới hạn/cách xử lý: pyarrow mới đòi NumPy 2, xung đột numpy==1.26.4 → cài "pyarrow<18"; BCTC.pdf và Nghị định 13 là PDF scan nên m1 bỏ qua (không xóa tài liệu); luật diagnosis Task 3 là heuristic trên văn bản, cần đọc answer/contexts thật khi viết failure_clusters.md.
- Nguồn/AI hỗ trợ nếu có: Claude Code hỗ trợ đọc yêu cầu, viết code Tasks 1–4, sửa m4 và soạn ghi chú commit/PR; Phi kiểm chứng bằng tests offline và validator của checker, tự đọc và giải thích được từng hàm trước khi nộp.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
