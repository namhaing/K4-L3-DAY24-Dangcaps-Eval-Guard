# Nhóm thực hiện K4 Track 3A

Tên nhóm: Dangcaps

Repo chung: https://github.com/namhaing/K4-L3-DAY24-Dangcaps-Eval-Guard

Trưởng nhóm/người nộp: Nguyễn Hải Nam — 2A202602476

Ngày lab/deadline áp dụng: 23:59 ngày 2026-10-12 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Hải Nam | 2A202602476 | Trưởng nhóm/tích hợp: môi trường full runtime, Qdrant, m2 + m3 (sửa fallback qdrant-client<1.10), bổ sung m5, sinh 50 answers, Task 7 cohen_kappa, Task 8 bias_report, merge nhánh, chạy batch A/B, TEAM.md, checker, nộp bài | Nhánh nam-setup: 00e8ffe (m2/m3), 0e13561 (Tasks 7–8), f938e3b (m5), 8c50995 (merge); artifacts/answers_50q.json |
| 2 | Đỗ Ngọc Phi | 2A202602531 | Tích hợp m1 + m4 (evaluator_models); Phase A Tasks 1–4; failure_clusters.md; blueprint Monitoring | Nhánh phi-phase-a, PR #2; src/m1_chunking.py, src/m4_eval.py, src/phase_a_ragas.py |
| 3 | Phạm Cường Quốc | 2A202602469 | Phase B Task 5 `pairwise_judge`, Task 6 `swap_and_average`; Phase C Task 11 `check_output_rail` | Nhánh cuongquoc_2A202602469, commit `48e38d1`; src/phase_b_judge.py, src/phase_c_guard.py; artifacts/judge_results.json (pairwise_results), artifacts/guard_results.json (output_results) |
| 4 | Nguyễn Trần Bảo Tâm | 2A202602408 | Tasks 9a/9b/10/12; blueprint kiến trúc và latency | Nhánh tam-guard; src/phase_c_guard.py; doc/reports/blueprint.md |

Người tích hợp/chạy batch/nộp link: Nguyễn Hải Nam — merge phi-phase-a, cuongquoc_2A202602469, tam-guard vào nam-setup (8c50995); chạy setup answers và runner A/B; Phase C dùng lại artifact live của Tâm vì nguồn không đổi.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler (máy Nam, máy chạy batch A/B): Windows 11 Home 10.0.26200, Python 3.11.9, Visual Studio Build Tools 2022 17.14 (MSVC 14.44.35207, Windows SDK 10.0.26100). Phải Repair VC++ Redistributable 14.38 (mất Package Cache) rồi nâng lên 14.51 mới cài được Build Tools.
Virtualenv/dependencies/imports: `py -3.11 -m venv .venv`; `pip install -r requirements/requirements.txt -c requirements/constraints-core.txt` (annoy 1.17.3 build bằng MSVC thành công). pip kéo pyarrow 26 cần NumPy 2 → cài `pyarrow==17.0.0`; pyarrow 17 kèm msvcp140.dll 14.28 làm torch 2.14.1 lỗi WinError 1114 → đổi tên DLL đó để dùng bản hệ thống 14.51. Sau đó `pip check`: No broken requirements; import ragas 0.1.22, nemoguardrails 0.10.0, presidio_analyzer, spacy 3.8.16, torch 2.14.1+cpu, numpy 1.26.4 OK; `pytest tests/ -q`: 86 passed.
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

### NguyenHaiNam-2A202602476

- Phần được giao và phần thực tế đã làm: trưởng nhóm/tích hợp. Viết checklist phân công 4 người (`doc/TEAM_CHECKLIST.md`); dựng môi trường full runtime trên Windows (Python 3.11.9, MSVC Build Tools + Windows SDK, NeMo 0.10.0, Qdrant v1.9.7 qua Docker); đưa m2 `HybridSearch` + m3 `CrossEncoderReranker` từ Day 18 và sửa m2 fallback `client.search()` vì lab pin `qdrant-client<1.10` không có `query_points()`; bổ sung m5 `enrich_chunks` (không nhánh nào có, setup bắt buộc); implement Task 7 `cohen_kappa` và Task 8 `bias_report`; merge ba nhánh phi-phase-a, cuongquoc_2A202602469, tam-guard; sửa phần đổi model sang `gpt-6-luna` (generation/judge/m5) và giữ evaluator RAGAS ở `gpt-4o-mini`; sinh 50 answers và chạy batch A/B; điền TEAM, chạy checker, nộp bài.
- Bằng chứng: nhánh nam-setup — `00e8ffe` (m2/m3), `8c50995` (merge nhóm), `0e13561` (Tasks 7–8), `f938e3b` (m5), `8cc1b3f` (TEAM), `4c1ed9c` (model gpt-6-luna); artifacts/answers_50q.json, ragas_50q.json, judge_results.json.
- Cách kiểm tra: `python -m pytest tests/ -q` → 86 passed (offline, mock); đối chiếu `cohen_kappa` với `binary_kappa` của checker trên 500 bộ nhãn ngẫu nhiên đều khớp. Smoke live: m2+m3 trên Qdrant thật (top-1 đúng câu nghỉ phép, rerank 0.997); m4 với evaluator gpt-4o-mini cho 4 metric hữu hạn; pairwise và binary judge gpt-6-luna trả JSON hợp lệ. Batch live chạy bằng `scripts/setup_answers.py --live` và `scripts/run_experiments.py --phase a/b --live`; `python scripts/check_lab.py` để xác nhận.
- Điều đã học: κ đo mức đồng thuận vượt trên may rủi nên quan trọng hơn tỷ lệ trùng nhãn khi phân bố nhãn lệch (6/4); A/B/tie và nhãn 0/1 là hai câu hỏi khác nhau; position bias chỉ phát hiện được khi swap và phải quy winner/scores lượt 2 về A/B gốc; verbosity chỉ là dấu hiệu thống kê, cần đọc nội dung. Về vận hành: provenance model phải tách theo vai trò, và hash nguồn phụ thuộc byte nên line ending (CRLF/LF) có thể làm artifact bị coi là stale.
- Giới hạn/cách xử lý: (1) VC++ Redistributable 14.38 mất Package Cache làm Build Tools lỗi 1603 → Repair bằng đúng bản 14.38 rồi nâng 14.51. (2) pyarrow 26 đòi NumPy 2 → `pyarrow==17.0.0`; pyarrow 17 kèm msvcp140.dll 14.28 làm torch lỗi WinError 1114 → đổi tên DLL để dùng bản hệ thống. (3) gpt-6-luna chỉ nhận temperature=1 và `max_completion_tokens`: RAGAS 0.1.22 ép temperature=1e-8 làm cả 4 metric NaN → evaluator giữ gpt-4o-mini; m5 với budget 400 token trả rỗng do reasoning tokens → nới budget. (4) Flashrank mặc định là model tiếng Anh → giữ CrossEncoder đa ngôn ngữ. (5) Fixtures checkout CRLF trước khi có `.gitattributes` làm Phase C bị báo stale → checkout lại bản LF, không sửa nội dung.
- Nguồn/AI hỗ trợ nếu có: Claude Code hỗ trợ đọc đề/rubric, lập checklist, chẩn đoán lỗi cài đặt, viết Tasks 7–8, sửa m2/m4/m5, tích hợp nhánh và soạn tài liệu; một phần đổi model do Codex bắt đầu. Nam kiểm chứng bằng unit tests, đối chiếu với checker, chạy smoke/API thật và đọc lại từng thay đổi trước khi commit.

### PhamCuongQuoc-2A202602469

- Phần được giao và phần thực tế đã làm: theo checklist được giao m5, Tasks 5/6/11, `bias_report.md` và mục CI gates của blueprint. Thực tế đã làm: Task 5 `pairwise_judge` (prompt chấm theo reference với 3 tiêu chí chính xác — đúng phiên bản và phủ định —, đầy đủ, súc tích; nêu rõ độ dài không phải lý do thắng; cho phép `tie`; `response_format=json_object`; kiểm tra winner ∈ {A, B, tie} và scores trong [0, 1]), Task 6 `swap_and_average` (gọi lượt 2 với B/A cùng reference, quy winner và scores lượt 2 về A/B gốc, đồng thuận thì giữ winner, lệch thì `tie`), Task 11 `check_output_rail` (answer là message cuối, chỉ chạy rail output, quyết định theo `activated_rails[].stop`, giữ nguyên answer sạch, thay bằng response của rail khi bị chặn). m5 và `bias_report.md` do Nam bổ sung, bản nháp CI gates do Tâm viết.
- Bằng chứng: commit `48e38d1` trên nhánh cuongquoc_2A202602469, được Tâm merge ở `a59a02d` và Nam tích hợp ở `8c50995`; kết quả live: `pairwise_results` 5 cặp × 2 lượt trong artifacts/judge_results.json, `output_results` 4/4 đúng trong artifacts/guard_results.json.
- Cách kiểm tra: `python -m pytest tests/test_phase_b.py -k "pairwise or swap" -q` (3 tests) và `python -m pytest tests/test_phase_c.py -k output -q` (2 tests) đều pass với SDK/NeMo mock; live Phase C (Tâm chạy) giữ nguyên hai output sạch 201/202 và chặn 203/204. Khi đổi judge sang gpt-6-luna, Nam bỏ `temperature=0` vì model chỉ nhận giá trị mặc định; logic Tasks 5/6 giữ nguyên.
- Điều đã học: winner A/B/tie là phép so sánh tương đối giữa hai candidate, khác nhãn tốt/xấu 0/1; position bias chỉ lộ ra khi hoán vị thứ tự, nên lượt 2 phải quy về không gian A/B gốc trước khi so sánh; output rail kiểm tra an toàn nội dung (PII, credential) chứ không thay thế kiểm tra faithfulness theo contexts.
- Giới hạn/cách xử lý: m5, `bias_report.md` và CI gates chưa được Quốc nộp trước giờ tích hợp nên Nam/Tâm bổ sung để kịp chạy setup và nộp; phần này không tính là đóng góp của Quốc. Judge dùng một model và mẫu nhỏ (5 cặp), nên kết quả pairwise chỉ mang tính tham khảo.
- Nguồn/AI hỗ trợ nếu có: phần mô tả này do Nam soạn từ diff commit `48e38d1` và kết quả tests/live; Quốc cần đọc lại, tự khai báo công cụ AI đã dùng (nếu có) và xác nhận trước khi nộp.

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
