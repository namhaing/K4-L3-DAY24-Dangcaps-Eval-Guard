# Kiểm chứng phần Tâm — 2026-10-12

Người phụ trách: Nguyễn Trần Bảo Tâm — 2A202602408. Múi giờ Asia/Ho_Chi_Minh.

## Code và bằng chứng đóng góp

Merge `a59a02d` trên tam-guard giữ code Tâm tại `359c675`, tích hợp Phi
(`468f478`: m1/m4, Tasks 1–4, TEAM) và Quốc (`48e38d1`: Tasks 5/6/11).
Không khai phần code của hai thành viên thành phần Tâm. Tâm hỗ trợ tích hợp,
chuẩn bị runtime guard, chạy/tinh chỉnh C và cập nhật blueprint/INDIVIDUAL.
Tại fetch cuối, origin/main và origin/nam vẫn ở `01bd8de`; Tasks 7/8 chưa có
implementation để review.

## Kết quả đã kiểm chứng

| Kiểm tra | Kết quả | Phạm vi |
|---|---|---|
| tests/test_phase_c.py | 12 passed | Mock/offline, gồm output rail của Quốc |
| tests/test_report_contracts.py | 30 passed | Offline, sau cố định kiểu xuống dòng |
| Toàn bộ tests/ | 83 passed, 3 failed, 3 deselected | Fail tại hai case kappa và một case bias của Tasks 7/8 còn TODO |
| Presidio thật | 12/12 | Tám clean không PII; bốn PII cases được phát hiện/anonymize |
| Smoke input hiện hành | 13/13 | 12 Presidio + attack 5 qua NeMo, scope smoke |
| Regression sau chỉnh prompt | 3/3 | Hai off-topic bị chặn, hỏi password length được allowed |
| Batch C cuối | 20/20 attacks, 8/8 clean, 4/4 output | Live, validator strict đã pass |
| Latency C cuối | 20 samples, 2 warm-up, P95 857.01ms | Input layers sequential; budget 500ms, flag false |
| OpenAI connectivity probe | Passed | gpt-4o-mini-2024-07-18 trả về từ probe |
| FastEmbed model | Passed, 384 chiều | all-MiniLM-L6-v2 thật, cache trên D |
| pip check / guard imports | Passed | Không còn broken requirements |
| check_lab.py | PASS Phase C; 10 failed checks khác | Pipeline/A/B/TEAM/báo cáo chung chưa hoàn tất |

## Hai lượt C và prompt

`guard_results_initial.json` giữ lượt đầu: 18/20 attacks, 7/8 clean,
4/4 output, P95 828.69ms. Off-topic 11/15 lọt; clean 107 về quy tắc
độ dài mật khẩu bị chặn bởi NeMo. Tâm làm rõ strict closed-domain scope và
phân biệt password RULE/VALUE trong self_check_input. Không sửa fixtures,
không dùng id/expected để ra quyết định.

Ba ca lỗi đạt regression 3/3, sau đó chạy lại toàn bộ C với cấu hình mới.
`guard_results.json` là lượt cuối, created_at=2026-10-12T12:37:26.122253+00:00
(2026-10-12 19:37:26 UTC+07); models.guard=[gpt-4o-mini], run_kind=live,
format_version=2. Tất cả 20 attacks và tám clean đạt, output 4/4.
Đạt điều kiện bonus C. Latency vẫn vượt target; không chọn lại mẫu để làm đẹp số.
Prompt được tinh chỉnh trên bộ lab, cần held-out độc lập để đánh giá tổng quát.

Bằng chứng bổ sung: `tam_presidio_smoke.json`, `tam_guard_smoke.json`
(phiên bản package và SHA-256 của source/config/fixtures), `tam_api_probe.json`,
`tam_prompt_regression.json`. `tam_guard_smoke_initial.json` giữ smoke trước
sửa prompt. Smoke/probe không thay artifact C chính thức. Mỗi baseline phản ánh
cấu hình tại thời điểm chạy; hash baseline không dùng để đối chiếu cấu hình mới.

## Môi trường thật

Windows, Python 3.11.9. Guard venv có Presidio analyzer/anonymizer 2.2.364,
spaCy 3.8.16, en_core_web_lg 3.8.0, NeMo 0.10.0, OpenAI SDK 1.109.1,
Annoy 1.17.3, FastEmbed 0.9.0, ONNX Runtime 1.31.0, NumPy 1.26.4.
Unit tests dùng interpreter python ngoài venv (guard venv chưa cài pytest).
Đây là runtime guard đã chạy; không khẳng định full RAG/Qdrant đã sẵn sàng.

Annoy ban đầu không build vì thiếu MSVC. Microsoft C++ Build Tools 2022
17.14.41 và Windows SDK 10.0.22621 đã cài thành công; vswhere báo isComplete=true,
isRebootRequired=false. Compiler/cache/shared components nằm ở
`D:\CodexBuildTools`; SDK dùng Windows Kits trên C. MSVC tools 14.44.35207.
Đã build wheel Annoy cp311-win_amd64 và import thành công.

Các lỗi setup đã giải quyết: installer ban đầu cần 6,71 GB trên C; đường dẫn
repo quá dài; SDK vẫn cần 2,75 GB trên C. Chuyển nguyên cache pip 1,34 GB từ
`C:\Users\ADMIN\AppData\Local\pip\Cache` sang `D:\CodexBuildTools\pip-cache`
và cấu hình pip dùng cache mới; C còn 3,68 GB sau chuyển. Không xóa cache.
FASTEMBED_CACHE_PATH trong .env trỏ đến .venv-guard/model-cache trên D; model
đã embed thành công. Key/venv/model cache không đưa vào Git.

Probe API đầu tiên trả HTTP 401; kiểm tra lại lúc 18:49 thành công ở endpoint
OpenAI chính thức. Các calls NeMo/C sau đó đã chạy được. Không có biến môi trường
ghi đè key; không lưu key hoặc thông báo lỗi provider chứa credential fragments.

.gitattributes cố định LF cho fixtures/source/config và bảo toàn byte artifacts
JSON. Fixtures giống byte của HEAD, không thay nội dung. Quy tắc tránh hash sai
do CRLF/LF giữa Windows/macOS/Linux, cả khi A/B dùng answers JSON làm nguồn.

## Bàn giao và lệnh tái kiểm chứng

```powershell
python -m pytest tests/test_phase_c.py tests/test_report_contracts.py -q
.\.venv-guard\Scripts\python.exe -m pip check
.\.venv-guard\Scripts\python.exe scripts/smoke_guard.py --live --nemo-limit 1 --output artifacts/tam_guard_smoke.json
python scripts/check_lab.py
```

Tâm đã hỗ trợ chạy C theo yêu cầu hoàn tất phần guard/latency; Nam dùng lại JSON
khi nguồn liên quan giữ nguyên, chạy A/B sau khi pipeline và answers đủ.
Không chạy integration hoặc batch C thêm nếu không có thay đổi/lỗi cần kiểm chứng.

Các phần chung còn thiếu: m2_search, m3_rerank, m5_enrichment, Tasks 7/8,
answers_50q.json, ragas_50q.json, judge_results.json, thông tin chung TEAM,
failure_clusters và bias_report. Nam/Phi/Quốc cần hoàn tất phần được phân công.
Blueprint còn chờ metadata/metric A/B; Tâm review Nam khi có code và cập nhật
số liệu chung sau đó. Các ngưỡng/workflow CI/monitoring trong blueprint là đề xuất.
