# Checklist phân công — K4 Track 3A Day 24 (Eval + Guardrail)

Tài liệu nội bộ của nhóm 4 người. Tổng hợp từ README, `doc/ASSIGNMENT.md`, `doc/RUBRIC.md`,
`doc/CHECKPOINTS.md`, `doc/REPORT_SCHEMAS.md`, `doc/SUBMISSION.md`, các test trong `tests/`
và checker `scripts/check_lab.py` / `src/report_contracts.py`.

> Tick `[x]` khi xong và ghi commit SHA bên cạnh nếu có. **Mọi người đều phải có commit**
> trong repo chung (rubric dùng git history làm bằng chứng đóng góp cá nhân).

---

## 0. Nguyên tắc chia đều

Mỗi thành viên nhận **cùng một "gói" công việc**:

1. Một phần chuẩn bị trước lớp (môi trường / tích hợp module RAG).
2. Một cụm hàm TODO có điểm trong `src/phase_*.py` + unit test tương ứng.
3. Một báo cáo Markdown (hoặc một phần báo cáo) điền từ kết quả thật.
4. Review chéo PR của một người khác.
5. Mục `INDIVIDUAL` của bản thân trong `doc/TEAM.md`.

### Bảng phân công

| | **Nam — Trưởng nhóm** | **Phi** | **Quốc** | **Tâm** |
|---|---|---|---|---|
| Chuẩn bị trước lớp | Môi trường full runtime, Qdrant, tích hợp **m2 + m3**, sinh 50 answers | Tích hợp **m1 + m4** (thêm `evaluator_models`) | Tích hợp **m5**, môi trường test offline mẫu cho nhóm | Thử Presidio/NeMo thật trên máy Nam (hoặc tự cài), chuẩn bị dữ liệu thử guard |
| Hàm có điểm | Task 7 `cohen_kappa`, Task 8 `bias_report` | Tasks 1–4 (Phase A) | Task 5 `pairwise_judge`, Task 6 `swap_and_average`, Task 11 `check_output_rail` | Task 9a `pii_scan`, 9b `check_input_rail`, 10 `run_adversarial_suite`, 12 `measure_p95_latency` |
| Điểm rubric của phần code | 15 | 30 | 25 | 30 |
| Báo cáo | `doc/TEAM.md` (phần chung) | `failure_clusters.md` + blueprint mục **Monitoring và cải tiến** | `bias_report.md` + blueprint mục **CI gates đề xuất** | blueprint mục **Kiến trúc** + **Latency**, tổng hợp blueprint |
| Chạy live | Chạy 3 batch chính thức A/B/C | Kiểm tra `ragas_50q.json` | Kiểm tra `judge_results.json` | Thử live nhỏ guard + tinh chỉnh `guardrails/config.yml`, kiểm tra `guard_results.json` |
| Review PR của | Phi | Quốc | Tâm | Nam |
| Thời lượng ước tính | ~5,5–6h | ~5,5h | ~5,5h | ~5,5h |

Nam có phần code ít điểm hơn vì đảm nhận việc tiền đề nặng nhất (môi trường + 50 answers + chạy batch + nộp bài).
Thiếu `answers_50q.json` thì Phase A bị 0 điểm, nên phần này có trọng số ngang một phase.

---

## 1. Việc chung cả nhóm (trước buổi học)

- [ ] Thống nhất **Tên nhóm** (không dấu, không khoảng trắng) → repo `K4-L3-DAY24-TenNhom-Eval-Guard`.
- [ ] Nam tạo repo chung, mời 3 thành viên làm collaborator.
- [ ] Mỗi người clone, tạo nhánh riêng: `nam-setup`, `phi-phase-a`, `quoc-judge`, `tam-guard`.
- [ ] Quy ước: commit bằng tài khoản GitHub của chính mình, mở PR về `main`, người review approve rồi Nam merge.
- [ ] Không commit `.env`, `.venv/`, cache model, API key. Kiểm tra `git status` trước mỗi commit.
- [ ] Thống nhất **chỉ Nam chạy batch live chính thức** (tránh trả phí 2 lần và lệch `source_sha256`).
- [ ] Mỗi người tạo môi trường **test offline** (không cần compiler/NeMo/model) theo hướng dẫn Quốc:

```powershell
py -3.11 -m venv .venv-tests
.\.venv-tests\Scripts\python.exe -m pip install -r requirements/requirements-test.lock.txt
.\.venv-tests\Scripts\python.exe -m pytest tests/ -m support -q
```

- [ ] Mỗi người đọc: `doc/ASSIGNMENT.md` (phần của mình), `doc/RUBRIC.md`, `doc/REPORT_SCHEMAS.md`, test tương ứng trong `tests/`.

### Quy tắc khi sửa chung một file

- `src/phase_b_judge.py`: Quốc làm Task 5–6, Nam làm Task 7–8 → mỗi người chỉ sửa hàm của mình, rebase trước khi PR.
- `src/phase_c_guard.py`: Tâm làm 9a/9b/10/12, Quốc làm Task 11 → tương tự.
- `doc/reports/blueprint.md`: Tâm tạo khung trước, Phi/Quốc điền mục của mình, Tâm hợp nhất cuối.

---

## 2. Nam — Trưởng nhóm: môi trường, answers, Task 7–8, nộp bài

### 2.1 Môi trường full runtime (máy chạy live chính thức)

- [ ] Cài **Python 3.11** (NeMo 0.10.0 chỉ hỗ trợ tới 3.11).
  ⚠️ Máy hiện tại chỉ có Python 3.12 và 3.10 (`py -0`) → phải cài thêm 3.11.
- [ ] Cài **Microsoft C++ Build Tools** (workload *Desktop development with C++*: MSVC + Windows SDK) để build `annoy==1.17.3`.
- [ ] Tạo venv và cài:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements/requirements.txt -c requirements/constraints-core.txt
.\.venv\Scripts\python.exe -m pip check
```

- [ ] `python -c "import ragas, nemoguardrails, presidio_analyzer, spacy; print('imports OK')"`
- [ ] `python -m spacy download en_core_web_lg`
- [ ] `docker compose -f infra/docker-compose.yml up -d` (Qdrant `v1.9.7`, port 6333; Docker 28.5.1 đã có sẵn trên máy).
- [ ] Tạo `.env` từ `.env.example`, điền `OPENAI_API_KEY` (không commit).
- [ ] Ghi kết quả thật (OS, Python, compiler, pip check, import, model download) cho mục "Môi trường" của `doc/TEAM.md`. Lỗi cài đặt thì ghi lỗi thật.

### 2.2 Tích hợp m2 + m3 (theo `doc/PIPELINE_INTERFACE.md`)

- [ ] Chép `m2_search.py`, `m3_rerank.py` vào `src/`.
- [ ] m2 `HybridSearch()` có `index(chunks)` (chunks là list dict `text`, `metadata`) và `search(question)` → object `.text`, `.score`, `.metadata`.
- [ ] m3 `CrossEncoderReranker().rerank(question, docs, top_k=...)` → list object có `.text`; `[]` thì setup dùng top 3 search.
- [ ] Tải/cache BGE-M3 + reranker trước lớp.

### 2.3 Sinh 50 answers (sau khi Phi, Quốc merge m1/m4/m5)

- [ ] `python scripts/setup_answers.py --live`
- [ ] Kiểm tra `artifacts/answers_50q.json`:
  - [ ] 50 id, factual=20 / multi_hop=20 / adversarial=10; `question`/`distribution`/`ground_truth` khớp test set.
  - [ ] `contexts` là list chuỗi **không rỗng** (checker từ chối chuỗi trắng).
  - [ ] `generation_mode` ∈ {`llm`, `extractive_fallback`}; `generation_model` là ID khi `llm`, `null` khi fallback.
  - [ ] Answer không phải ground_truth; đếm số câu fallback và báo Phi.
- [ ] Commit `answers_50q.json`, báo cả nhóm pull.

### 2.4 Task 7 + Task 8 trong `src/phase_b_judge.py` (15đ)

- [ ] **Task 7 `cohen_kappa(judge_labels, human_labels)`** (10đ): tính p_o, p_e; trả float trong [-1, 1]; xử lý p_e = 1 (tránh chia 0). Test: khớp hoàn toàn → 1; ngược hoàn toàn → −1; `[1,1,0,0]` vs `[1,0,1,0]` → 0.
- [ ] **Task 8 `bias_report(judge_results)`** (5đ):
  - [ ] `total_judged`, `position_bias_count` (số case `position_consistent=False`), `position_bias_rate`.
  - [ ] `verbosity_details`: `a_wins_a_longer`, `b_wins_b_longer`, `total_decisive` (dựa `final_winner` và `len()` chuỗi).
  - [ ] `verbosity_bias` = (a_wins_a_longer + b_wins_b_longer) / decisive, 0 nếu decisive = 0.
  - [ ] `interpretation` không rỗng; list rỗng → `total_judged = 0`.
- [ ] `python -m pytest tests/test_phase_b.py -k "kappa or bias" -q` pass; PR → Tâm review.

### 2.5 Chạy batch live chính thức

- [ ] `python -m pytest tests/ -q` → toàn bộ pass (mỗi student test fail = −3đ).
- [ ] `python scripts/run_experiments.py --phase a --live`
- [ ] `python scripts/run_experiments.py --phase b --live`
- [ ] `python scripts/run_experiments.py --phase c --live --latency-samples 20`
- [ ] **Không** chạy thêm `pytest -m integration --run-live` sau runner (tốn phí lặp).
- [ ] Nếu đổi answers/fixtures sau khi chạy → chạy lại phase liên quan (checker so SHA-256).
- [ ] Commit 3 JSON, báo Phi/Quốc/Tâm kiểm tra và điền báo cáo.

### 2.6 TEAM.md và nộp bài

- [ ] Điền tên nhóm, link repo, trưởng nhóm + MSSV, deadline, bảng 4 thành viên (MSSV **không trùng**), người tích hợp, môi trường.
- [ ] Có `## INDIVIDUAL` với 4 tiêu đề `### HoVaTenKhongDau-MSSV` (checker yêu cầu kết thúc bằng `-MSSV`).
- [ ] `python scripts/check_lab.py --with-tests` → `0 failed checks`.
- [ ] Kiểm tra bảo mật:

```bash
git check-ignore artifacts/answers_50q.json artifacts/ragas_50q.json artifacts/judge_results.json artifacts/guard_results.json
git status --short
git rev-parse HEAD
```

- [ ] Push, mở đúng commit trên GitHub; ghi commit SHA vào TEAM; nộp link qua vlearn trước **23:59 ngày lab (UTC+07:00)**.
- [ ] Review PR của Phi. Viết INDIVIDUAL của mình.

---

## 3. Phi — m1 + m4, Phase A, báo cáo lỗi, blueprint Monitoring

### 3.1 Tích hợp m1 + m4 (trước lớp)

- [ ] Chép `m1_chunking.py`, `m4_eval.py` vào `src/`.
- [ ] m1 `load_documents()` → list dict `text`, `metadata`, đọc từ `config.DATA_DIR`.
- [ ] m1 `chunk_hierarchical(text, metadata=...)` → `(parents, children)`; child có `.text`, `.metadata`, `.parent_id`.
- [ ] m4 `evaluate_ragas(questions, answers, contexts, ground_truths)` → dict có `per_question` (object có 4 metric, float Python hữu hạn [0,1]).
- [ ] **Sửa m4 trả thêm `metadata.evaluator_models`** = list model IDs LLM + embedding thực sự dùng trong lượt RAGAS. Không lấy `JUDGE_MODEL` thay.
- [ ] m4 trả dict → `SimpleNamespace(**record)`; scalar NumPy → `float(...)`; không thay NaN bằng điểm giả.
- [ ] Không xoá tài liệu policy bản cũ trong `data/` (bẫy có chủ ý).

### 3.2 Tasks 1–4 trong `src/phase_a_ragas.py` (30đ) — xoá hết `# TODO`

- [ ] **Task 1 `group_by_distribution`** (5đ): 3 key `factual`, `multi_hop`, `adversarial`; 20/20/10.
- [ ] **Task 2 `run_ragas_50q`** (10đ):
  - [ ] `from src.m4_eval import evaluate_ragas` **bên trong hàm** (test thay `sys.modules["src.m4_eval"]`).
  - [ ] Gọi `evaluate_ragas` đúng 1 lần với 4 list theo đúng thứ tự answers.
  - [ ] Kiểm `len(per_question) == len(answers)` trước khi ghép.
  - [ ] Bọc `float(...)`; NaN/ngoài [0,1] → raise.
  - [ ] Trả `RagasEvaluation(results, raw["metadata"]["evaluator_models"])`; thiếu metadata → raise.
- [ ] **Task 3 `bottom_10`** (7đ): sắp tăng theo `avg_score`, tối đa 10; row có `rank`, `question_id`, `distribution`, `question`, `avg_score` (≥4 chữ số thập phân; checker cho sai số 1e-4), `worst_metric`, `diagnosis`, `suggested_fix` không rỗng. Nên viết diagnosis cụ thể hơn `DIAGNOSTIC_TREE` (ví dụ nêu bẫy phiên bản với câu adversarial).
- [ ] **Task 4 `cluster_analysis`** (8đ):
  - [ ] `matrix[worst_metric][distribution]` đếm **mọi câu**.
  - [ ] `distribution_avg_scores`, bỏ nhóm rỗng khỏi phép chia.
  - [ ] `dominant_failure_distribution` = nhóm có **mean thấp nhất** (không phải nhóm đông nhất).
  - [ ] `dominant_failure_metric` = metric có tổng hàng lớn nhất; `insight` không rỗng.
- [ ] `python -m pytest tests/test_phase_a.py -q` → 6 test pass; PR → Nam review.

### 3.3 `doc/reports/failure_clusters.md` (sau khi có `ragas_50q.json`)

- [ ] Header: tên nhóm, người phụ trách + MSSV, `created_at`, generation mode/fallback, models generation + evaluator.
- [ ] Bảng 4 metric + avg_score × 3 distribution (từ `per_distribution`).
- [ ] Bảng **10 dòng bottom 10** giữ nguyên diagnosis/suggested_fix của Task 3.
- [ ] Đọc thật answer/contexts/ground_truth của câu đại diện → phân biệt lỗi retrieval / generation / phiên bản / phủ định.
- [ ] Matrix 4 × 3; nhóm yếu nhất theo mean + giá trị; worst metric phổ biến nhất + số câu; đề xuất sửa + cách đo lại.
- [ ] Mục adversarial: so sánh với factual/multi_hop. **Bonus A (+4đ)**: adversarial mean < factual mean **kèm phân tích bẫy**.
- [ ] Giới hạn: 50 câu, model evaluator, fallback.

### 3.4 Blueprint — mục "Monitoring và cải tiến"

- [ ] Metric theo dõi, ngưỡng cảnh báo, cách lấy mẫu, xử lý false positive, drift, privacy, người xử lý.
- [ ] Điền: RAGAS mean/worst distribution, κ (lấy từ Quốc), attacks passed/20, false_positive_rate (lấy từ Tâm).
- [ ] 3–5 đề xuất cải tiến có thể kiểm chứng, gắn với bằng chứng của nhóm; nêu giới hạn bộ 50/20/8/4.
- [ ] Review PR của Quốc. Viết INDIVIDUAL của mình.

---

## 4. Quốc — m5, Task 5–6 (judge), Task 11 (output rail), báo cáo bias, blueprint CI

### 4.1 Tích hợp m5 + hướng dẫn môi trường test (trước lớp)

- [ ] Chép `m5_enrichment.py` vào `src/`.
- [ ] `enrich_chunks(chunks)` giữ **đúng số lượng và thứ tự**; item có `.enriched_text`, `.auto_metadata`; `[]` = fallback. Nếu m5 gộp/tách chunk → viết adapter ánh xạ rõ.
- [ ] Dựng thử `.venv-tests`, ghi lại lệnh chạy đúng trên Windows, gửi nhóm.

### 4.2 Task 5 + Task 6 trong `src/phase_b_judge.py` (20đ)

- [ ] **Task 5 `pairwise_judge(q, A, B, reference="")`** (10đ):
  - [ ] `from openai import OpenAI` và `OpenAI()` **bên trong hàm** (test thay `sys.modules["openai"]`).
  - [ ] Gọi `chat.completions.create` đúng 1 lần, model `JUDGE_MODEL`, `response_format={"type": "json_object"}`, nên `temperature=0`.
  - [ ] **Reference nằm trong messages** (test kiểm tra).
  - [ ] Prompt chấm accuracy (theo reference, đúng phiên bản/phủ định), completeness, conciseness; nhắc "độ dài không phải lý do thắng".
  - [ ] Trả `{"winner", "reasoning", "scores": {"A", "B"}}`; validate winner ∈ {A, B, tie}, scores ∈ [0,1].
  - [ ] Đổi model judge → cập nhật `JUDGE_MODEL` trong module.
- [ ] **Task 6 `swap_and_average`** (10đ):
  - [ ] Pass 1 `pairwise_judge(q, A, B, reference=...)`, pass 2 `pairwise_judge(q, B, A, reference=...)` (3 tham số đầu **positional**).
  - [ ] Đổi winner pass 2 về gốc (A↔B, tie giữ); scores pass 2 → `{"A": raw["B"], "B": raw["A"]}`.
  - [ ] `final_winner` = winner nếu 2 lượt khớp, ngược lại `tie`; `position_consistent` tương ứng.

### 4.3 Task 11 trong `src/phase_c_guard.py` (5đ)

- [ ] **`check_output_rail(question, answer, rails)`** async:
  - [ ] messages = user question + assistant answer (answer là message **cuối**); `options={"rails": ["output"], "log": {"activated_rails": True}}`.
  - [ ] Flag theo `result.log.activated_rails` (`rail.stop`), không dò từ khoá.
  - [ ] `safe`, `flagged_reason`, `final_answer` = response của rail nếu flag, ngược lại giữ answer gốc.
  - [ ] Thử live cùng Tâm: 201, 202 giữ nguyên (202 có `helpdesk@cty.vn` hợp lệ); 203, 204 bị thay/redact.
- [ ] `python -m pytest tests/test_phase_b.py -k "pairwise or swap" -q` và `python -m pytest tests/test_phase_c.py -k output -q` pass; PR → Phi review.

### 4.4 `doc/reports/bias_report.md` (sau khi có `judge_results.json`)

- [ ] Header: tên nhóm, người phụ trách + MSSV, `created_at`, models generation/judge.
- [ ] Nguồn cố định 5 cặp id **1, 5, 12, 21, 41**: A = `answers_50q.json:answer`, B = `human_labels_10q.json:model_answer`, reference = `test_set_50q.json:ground_truth`.
- [ ] Bảng 5 cặp: id, winner_pass1, winner_pass2 (đã quy về gốc), final_winner, position_consistent, reasoning + scores 2 lượt.
- [ ] Position bias count/rate; verbosity win rate + số decisive; phân biệt dấu hiệu thống kê với kết luận nguyên nhân.
- [ ] Bảng 10 dòng calibration đúng thứ tự JSON: question_id, model_answer, nhãn judge, reasoning, human_label, agree. Xác nhận không leak `human_label`/`human_note`.
- [ ] κ, p_o, p_e, diễn giải Landis–Koch. **Bonus B (+3đ)**: κ > 0.6.
- [ ] Giới hạn: 5 cặp, 10 nhãn, một model judge.

### 4.5 Blueprint — mục "CI gates đề xuất"

- [ ] Gate: faithfulness ≥ 0.75, avg_score ≥ 0.65; attacks ≥ 18/20, clean 8/8, output đúng; full guard P95 < 500ms chỉ khi đã đo full guard.
- [ ] Đề xuất lệnh job + cách script trả exit code ≠ 0 khi không đạt; nêu MIN_* chỉ là biến đề xuất.
- [ ] Ghi rõ workflow **chưa triển khai** (hoặc dẫn bằng chứng nếu thực sự đã có).
- [ ] Review PR của Tâm. Viết INDIVIDUAL của mình.

---

## 5. Tâm — Guard input: Task 9a, 9b, 10, 12, tinh chỉnh guard, blueprint chính

### 5.1 Chuẩn bị (trước lớp)

- [ ] Có môi trường chạy được Presidio + NeMo thật: tự cài theo mục 2.1 hoặc dùng chung máy Nam.
- [ ] Đọc `guardrails/config.yml`, `guardrails/rails.co`, `fixtures/adversarial_set_20.json`, `clean_set_8.json`, `output_set_4.json`.

### 5.2 Hàm trong `src/phase_c_guard.py` (30đ)

- [ ] **Task 9a `pii_scan(text, analyzer, anonymizer)`** (10đ):
  - [ ] `analyzer.analyze(text=..., language=PRESIDIO_LANGUAGE)` **chỉ 2 keyword này** (mock test không nhận `entities=`).
  - [ ] Trả `has_pii`, `entities` (`type`, `text`, `score`, `start`, `end`), `anonymized` (qua `anonymizer.anonymize(text=..., analyzer_results=...)`).
  - [ ] Không có PII → đúng `{"has_pii": False, "entities": [], "anonymized": text}`.
  - [ ] ⚠️ **Rủi ro chặn nhầm**: recognizer mặc định (PERSON, LOCATION, DATE_TIME, NRP…) với spaCy tiếng Anh có thể gắn nhầm "VPN", "MFA", "Senior", "v2024"… → **lọc kết quả sau analyze** theo allowlist (`VN_CCCD`, `VN_PHONE`, `EMAIL_ADDRESS`, `PHONE_NUMBER`…) rồi mới anonymize.
- [ ] **Task 9b `check_input_rail(text, rails)`** async (5đ):
  - [ ] `await rails.generate_async(messages=[{"role": "user", ...}], options={"rails": ["input"], "log": {"activated_rails": True}})`.
  - [ ] Block theo `rail.stop` trong `activated_rails`, **không** dò "xin lỗi/không thể" (clean 102 chứa đúng cụm này).
  - [ ] Trả `allowed`, `blocked_reason`, `response = result.response[0]["content"]`.
- [ ] **Task 10 `run_adversarial_suite(items, rails, analyzer, anonymizer)`** (10đ):
  - [ ] Hàm đồng bộ, `asyncio.run(...)` **một lần** cho cả batch.
  - [ ] Gọi `pii_scan(text, analyzer, anonymizer)` và `check_input_rail(text, rails)` **positional**, qua tên global của module (test monkeypatch bằng `lambda text, *args`).
  - [ ] PII → `blocked_by="presidio"` và **không gọi NeMo** (test đếm đúng 24 lần await).
  - [ ] Row: `id`, `category`, `input` (giữ nguyên), `expected`, `actual`, `blocked_by` (`presidio`/`nemo_input`/`None`), `passed`. Không dùng `expected` để quyết định.
- [ ] **Task 12 `measure_p95_latency(...)`** (5đ):
  - [ ] `time.perf_counter()` qua module `time` (test patch `phase.time.perf_counter`).
  - [ ] Một event loop; 2 warm-up thật (Presidio + NeMo) không tính; `n_runs` mẫu cycle input; **luôn đo cả 2 tầng**.
  - [ ] Sample: `presidio_ms`, `nemo_input_ms`, `input_guard_ms` = tổng; trả `summarize_latency(samples, warmup_runs=2)`.
- [ ] `python -m pytest tests/test_phase_c.py -q` pass (trừ phần output do Quốc); PR → Quốc review.

### 5.3 Thử live nhỏ + tinh chỉnh (trước khi Nam chạy batch C)

- [ ] `pii_scan` thật trên 8 câu clean → không câu nào `has_pii`.
- [ ] Input rail trên attack khó (id 5, 7, 16–20) và cả 8 clean.
- [ ] Clean bị chặn / attack lọt → chỉnh prompt `self_check_input` / `self_check_output` trong `guardrails/config.yml`; không sửa fixtures, không hard-code theo id/expected. Ghi lại thay đổi cho blueprint.
- [ ] Mục tiêu: attacks ≥ 15/20 (bắt buộc), **≥ 18/20 + clean 8/8 = bonus C (+3đ)**.

### 5.4 `doc/reports/blueprint.md` — tạo khung, viết Kiến trúc + Latency, hợp nhất

- [ ] Tạo khung sớm để Phi (Monitoring) và Quốc (CI gates) điền song song.
- [ ] Header: tên nhóm, người phụ trách (Tâm, Phi, Quốc + MSSV), `created_at`, guard models, models generation/evaluator/judge.
- [ ] **Kiến trúc + failure action**: Input → Presidio → NeMo input → RAG → NeMo output → response; hành động khi chặn, log/redact, nơi giữ secrets, fallback.
- [ ] **Latency**: n_samples, warmup_runs, percentile_method; bảng P50/P95/P99 Presidio, NeMo input, input guard sequential (số thật).
  - [ ] RAG / NeMo output / full guard ghi **"chưa đo"** + kế hoạch đo; không suy từ `input_guard_ms`.
  - [ ] `latency_budget_ok` + giá trị thật so 500ms; vượt thì ghi đúng và nêu bottleneck.
- [ ] Hợp nhất 3 mục, rà không còn placeholder / ô trống (blueprint giữ mẫu = −10đ).
- [ ] Review PR của Nam. Viết INDIVIDUAL của mình.

---

## 6. Lịch làm việc đề xuất

| Thời điểm | Nam | Phi | Quốc | Tâm |
|---|---|---|---|---|
| D-2 | Python 3.11, compiler, deps, spaCy, Qdrant; m2 + m3 | m1 + m4 (`evaluator_models`) | m5; hướng dẫn `.venv-tests` | Đọc guard config/fixtures; cài/mượn env |
| D-1 | Sinh 50 answers; code Task 7–8 | Code Task 1–4 + test | Code Task 5, 6, 11 + test | Code Task 9a, 9b, 10, 12 + test; thử live guard |
| 15' đầu buổi | Xác nhận env/answers; merge PR; điền TEAM | Review PR Quốc | Review PR Tâm | Review PR Nam |
| Phase A (30') | Chạy A live | Kiểm tra JSON, viết `failure_clusters.md` | Hỗ trợ đọc bottom 10 | Tinh chỉnh `config.yml` |
| Phase B (30') | Chạy B live | Hoàn thiện báo cáo A | Kiểm tra JSON, viết `bias_report.md` | Tạo khung blueprint |
| Phase C (30') | Chạy C live | Blueprint Monitoring | Blueprint CI gates | Kiểm tra JSON, blueprint Kiến trúc + Latency |
| Sau giờ (≤ 23:59) | TEAM, checker, push, nộp | INDIVIDUAL | INDIVIDUAL | Hợp nhất blueprint, INDIVIDUAL |

---

## 7. Checklist cuối trước khi nộp (Nam tick, cả nhóm cùng rà)

### Source

- [ ] `src/m1_chunking.py` … `src/m5_enrichment.py` có đủ.
- [ ] `src/phase_a_ragas.py`, `src/phase_b_judge.py`, `src/phase_c_guard.py` **không còn chuỗi `# TODO`** (−5đ/module).
- [ ] Không sửa `tests/`, `fixtures/`, `data/`, runner, checker để "qua bài".

### Artifacts (từ lượt chạy live thật)

- [ ] `answers_50q.json` — 50 câu, 20/20/10, generation_mode/model đúng.
- [ ] `ragas_50q.json` — 50 per_question, 10 bottom, matrix, evaluator models từ m4.
- [ ] `judge_results.json` — pair_sources, 5 cặp, 10 binary, κ, bias.
- [ ] `guard_results.json` — 20 attack (≥15 pass), 8 clean (FPR = 0), 4 output, latency ≥ 20 samples.

### Báo cáo + TEAM

- [ ] 3 báo cáo ≥ 200 ký tự, không `{{...}}`, không `[Họ...]`, không `?` thay số đo, không ô bảng trống.
- [ ] `doc/TEAM.md`: 4 thành viên, MSSV khác nhau, 4 mục `### HoVaTen-MSSV`, mục Nguồn/AI hỗ trợ, commit SHA, mục Cập nhật sau khi nộp.
- [ ] Số liệu trong báo cáo khớp JSON.

### Lệnh kiểm tra

- [ ] `python -m pytest tests/ -q` → pass toàn bộ.
- [ ] `python scripts/check_lab.py` → `0 failed checks`.
- [ ] `git shortlog -sn` → **cả 4 người đều có commit**.
- [ ] Không có `.env`, key, venv, cache; push; nộp link + commit SHA.

---

## 8. Tóm tắt điểm và lỗi dễ mất điểm

| Hạng mục | Điểm | Người | Lỗi hay gặp |
|---|---:|---|---|
| Phase A (T1–T4) | 30 | Phi | Thiếu answers = 0đ; m4 thiếu `evaluator_models`; chọn nhóm yếu theo số câu; NaN |
| Phase B T5–T6 | 20 | Quốc | Quên đổi winner/scores pass 2 về gốc; thiếu reference trong prompt |
| Phase B T7–T8 | 15 | Nam | Chia 0 khi p_e = 1; verbosity tính trên winner pass 1 thay vì final |
| Phase C T9a, 9b, 10, 12 | 30 | Tâm | Presidio chặn nhầm clean; dò từ khoá refusal; gọi NeMo khi đã bị Presidio chặn; thiếu warm-up |
| Phase C T11 | 5 | Quốc | Không giữ nguyên answer sạch |
| Blueprint (Task 13) | −10 nếu trống | Tâm, Phi, Quốc | Giữ placeholder; dùng `input_guard_ms` làm full guard |
| Bonus | +10 | Phi / Quốc / Tâm | A: adversarial < factual + phân tích (+4); B: κ > 0.6 (+3); C: ≥18/20 + clean 8/8 (+3) |
