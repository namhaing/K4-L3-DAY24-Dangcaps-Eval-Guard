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
| 4 | Nguyễn Trần Bảo Tâm | 2A202602408 | Tasks 9a/9b/10/12; blueprint kiến trúc và latency | Nhánh tam-guard; src/phase_c_guard.py; doc/reports/blueprint.md |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: {{Phiên bản thực tế}}.
Virtualenv/dependencies/imports: {{Lệnh và kết quả}}.
Models/Qdrant/50 answers đã chuẩn bị: {{Bằng chứng và giới hạn/fallback}}.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

### NguyenTranBaoTam-2A202602408

- Đã triển khai: pii_scan, check_input_rail, run_adversarial_suite, measure_p95_latency trong src/phase_c_guard.py; viết blueprint kiến trúc/failure action/latency, hỗ trợ tích hợp Phi và Quốc, cài runtime guard và tinh chỉnh self_check_input từ lỗi live.
- Bằng chứng: code Tâm tại `359c675`; merge `a59a02d` tích hợp Phi `468f478` và Quốc `48e38d1`; scripts/smoke_guard.py, artifacts/guard_results.json, các JSON smoke/regression và doc/reports/tam_guard_validation.md. Tasks 5/6/11 là code Quốc; m1/m4 và Phase A là code Phi.
- Kiểm tra: Phase C 12 tests offline, report contracts 30 tests; toàn repo 83 passed, 3 failed tại Tasks 7/8 còn TODO. Live C cuối 20/20 attacks, 8/8 clean (FPR=0), 4/4 output; validator strict pass. 20 latency samples, 2 warm-up; input guard P95=857.01ms, vượt budget 500ms, flag false. RAG/output/full guard chưa đo.
- Môi trường: Windows, Python 3.11.9, Presidio 2.2.364, spaCy 3.8.16 + en_core_web_lg 3.8.0, NeMo 0.10.0, OpenAI 1.109.1, Annoy 1.17.3, FastEmbed 0.9.0, ONNX Runtime 1.31.0. Đã cài MSVC/Windows SDK trên máy và chuyển cache pip/model sang D; pip check/import/model/API đều kiểm chứng thật.
- Phân tích lỗi: lượt C đầu 18/20 attacks, 7/8 clean, 4/4 output; hai off-topic lọt và câu hỏi password length bị chặn. Chỉnh prompt phạm vi đóng và RULE/VALUE, regression 3/3 rồi chạy lại C đạt 20/20, 8/8, 4/4. Giữ artifacts lượt đầu; không sửa dữ liệu fixtures hoặc hard-code expected/id.
- Điều cần nắm: PII block dừng trước NeMo trong request; latency đo luôn hai tầng và tính percentile từ tổng từng mẫu. Scope input_layers_sequential không là full guard. Source hashes cần byte ổn định khi Git checkout khác hệ điều hành. Bộ kiểm chứng nhỏ và đã dùng để chỉnh prompt, cần held-out độc lập.
- Còn chờ nhóm: Tasks 7/8 của Nam để review, artifacts A/B và phần Monitoring/CI tương ứng để hợp nhất blueprint. Task 11 của Quốc đã hợp nhất và kiểm chứng offline/live. Nam dùng lại artifact C khi nguồn giữ nguyên để tránh gọi API trùng.
- Nguồn/AI hỗ trợ: Codex hỗ trợ đọc yêu cầu, triển khai từ scaffold, tích hợp code nhóm, sửa môi trường, chạy tests/engine/API thật, viết smoke runner, tinh chỉnh prompt và tài liệu. Tâm cần tự đọc, giải thích và xác nhận đóng góp trước khi nộp.

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
