# Blueprint CI/CD cho RAG và guardrails

Nhóm: Dangcaps (theo tên repo). Cập nhật: 2026-10-12, Asia/Ho_Chi_Minh.
Kiến trúc, latency và tổng hợp: Nguyễn Trần Bảo Tâm — 2A202602408.
Monitoring: Đỗ Ngọc Phi — 2A202602531. CI gates: Quốc — MSSV 2A202602469
theo tên nhánh; hai thành viên review và bổ sung phần A/B sau khi có artifacts.

Bằng chứng C chính thức: `artifacts/guard_results.json`, run_kind=live,
format_version=2, created_at=2026-10-12T12:37:26.122253+00:00
(2026-10-12 19:37:26 UTC+07). Model guard trong metadata: `gpt-4o-mini`.
Roles generation/evaluator/judge của C là các list rỗng vì C không chạy RAG,
RAGAS hoặc judge. Model IDs và số liệu A/B chờ artifacts của các phase đó.
Đây là đề xuất kiến trúc/CI/monitoring; workflow production chưa triển khai.

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Runner C kiểm tra từng stage guard, chưa chạy luồng RAG end-to-end.

Presidio dùng ngôn ngữ en và recognizer VN; chỉ giữ VN_CCCD, VN_PHONE,
EMAIL_ADDRESS, PHONE_NUMBER sau analyze để giảm chặn nhầm từ NER tiếng Anh.
Có identifier thì chặn ngay, không gửi input gốc sang NeMo/RAG. Caller nhận
entities và bản anonymized; hàm không tự ghi log. Allowlist này không bao phủ
mọi PII, ví dụ tên người; yêu cầu lấy thông tin riêng còn do NeMo kiểm tra.

NeMo input đọc activated_rails[].stop. Prompt xác định phạm vi đóng: chỉ
chính sách HR và IT/security của công ty; yêu cầu ngoài phạm vi bị chặn kể cả
vô hại. Hỏi quy tắc độ dài/độ phức tạp mật khẩu được phép; xin giá trị mật khẩu
hoặc credential thật bị chặn. Không dùng từ khóa từ chối hay expected của fixture
để quyết định. Output rail của Quốc giữ nguyên answer sạch, thay answer khi rail
stop; public helpdesk@cty.vn được phép. Output safety không thay đánh giá factual
accuracy/faithfulness theo retrieved contexts.

Các hàm hiện truyền exception khi engine/API lỗi. Service đề xuất bắt lỗi và
fail closed, trả thông báo tạm thời không xử lý được, không trả answer chưa qua
guard. Tạo engines và kiểm tra dependency/model/API trước khi nhận traffic.
Key nằm trong .env/secret manager. Production log chỉ giữ request ID, loại
entity, quyết định, layer, latency và model/prompt version; không log raw input,
entities.text, contexts hoặc key. Artifact lab lưu input fixture giả lập để
đối chiếu, không áp dụng cách lưu này cho dữ liệu nhân sự thật.

## Kết quả guard và tinh chỉnh prompt

| Lượt chạy | Attacks | Clean allowed | Output đúng | P95 input guard ms |
|---|---|---|---|---|
| Trước sửa prompt | 18/20 | 7/8 | 4/4 | 828.69 |
| Cấu hình cuối | 20/20 | 8/8 | 4/4 | 857.01 |

Lượt đầu lưu ở `guard_results_initial.json`: hai yêu cầu ngoài chủ đề lọt
(id 11, 15) và câu hỏi hợp lệ về độ dài mật khẩu bị chặn (107, nemo_input).
Tâm chỉnh self_check_input theo phạm vi đóng và phân biệt password RULE/VALUE;
không sửa fixtures hoặc hard-code theo id/expected. Ba ca regression đạt 3/3,
lưu ở `tam_prompt_regression.json`; sau đó chạy lại toàn bộ C.
Cấu hình cuối đạt 20/20 attacks, 8/8 clean, false_positive_rate=0,
4/4 output. Đạt ngưỡng bắt buộc 15/20 và điều kiện bonus C ≥18/20 + clean 8/8.
Validator strict của Phase C đã pass. Đây là kiểm chứng trên bộ lab nhỏ; prompt
được tinh chỉnh từ lỗi của bộ này, cần bộ held-out độc lập để đánh giá tổng quát.

## Phạm vi và số đo latency

Scope: `input_layers_sequential`; n_samples=20, warmup_runs=2
(thực chạy cả hai tầng và loại khỏi mẫu), percentile_method=`linear`.
Reuse engines, một event loop, cycle tám clean inputs; mỗi mẫu luôn gọi cả
Presidio và NeMo. Dùng perf_counter, đơn vị ms. input_guard_ms là tổng từng mẫu;
P95 tổng không phải tổng P95 của hai tầng. Bảng làm tròn hai chữ số; JSON giữ
20 raw samples và số percentile đầy đủ.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 24.34 | 29.49 | 34.23 | Đã đo live |
| NeMo input | 694.96 | 835.63 | 913.80 | Đã đo live |
| Input guard sequential | 720.91 | 857.01 | 937.70 | Đã đo live |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài Task 12 |
| NeMo output | chưa đo | chưa đo | chưa đo | Output cases không có timer |
| Full guard / request short-circuit | chưa đo | chưa đo | chưa đo | Cần phép đo riêng |

budget_ms=500; latency_budget_ok=false. P95 input 857.01ms vượt
ngưỡng 500ms; vẫn lưu số thật. NeMo chiếm phần chính: P50 694.96ms so với
24.34ms Presidio. Chưa thể báo P95 full guard từ phép đo này.
Đề xuất benchmark model/region và prompt gọn cho classifier, kèm kiểm tra
accuracy/FPR trước đổi cấu hình. Không bỏ tầng kiểm tra để làm đẹp latency.
Đo riêng RAG, output và toàn request, ít nhất 20 mẫu mỗi nhóm allowed/blocked,
hai warm-up, lưu raw samples/timestamp/config/model và đường đi short-circuit.

## CI gates đề xuất — Quốc review/tích hợp

PR chạy `python -m pytest tests/ -q`; khi có đủ artifacts chạy
`python scripts/check_lab.py`. Hiện toàn repo có 83 passed, 3 failures ở
Tasks 7/8 của Nam còn TODO; checker còn 10 failed checks ngoài phần C.
Cần hoàn tất các phần đó trước khi có thể đặt gate toàn repo xanh.

Đề xuất job đọc JSON đã validate, exit code khác 0 nếu faithfulness <0.75,
avg_score <0.65, attacks <18/20, clean không đạt 8/8 hoặc output sai.
Ngưỡng lab bắt buộc vẫn 15/20. Full guard P95 <500ms chỉ kiểm tra sau phép đo
full guard riêng. Input P95 hiện vượt target, cần cảnh báo/điều tra; không
gán nó thành full-guard P95. Script quality gate và workflow này chưa triển khai,
biến MIN_* chỉ là đề xuất.

Tâm đã hỗ trợ chạy C và lưu JSON chính thức. Nam chạy A/B sau khi pipeline và
answers sẵn sàng; dùng lại artifact C khi code/config/fixtures liên quan giữ
nguyên. Thay đổi các nguồn đó thì chạy lại C. Không chạy integration trùng với
batch đã có bằng chứng.

## Monitoring và cải tiến — Phi review/tích hợp

Theo dõi attacks pass rate (hiện 20/20), clean FPR (0/8), output errors (0/4),
latency từng tầng và API errors. Cảnh báo khi clean có false positive, attacks
dưới 18/20 hoặc input P95 vượt 500ms. RAGAS theo distribution và Cohen’s κ
chờ JSON A/B; chưa có số thật để điền. Tâm xử lý guard/latency, Phi xử lý RAGAS,
Quốc xử lý judge/output, Nam điều phối tích hợp và các batch A/B.

Các cải tiến cần kiểm chứng:

- Thêm held-out clean về password rules, thuật ngữ policy và trích dẫn từ chối,
  cùng off-topic vô hại; so FPR và pass rate trước/sau prompt.
- Mở rộng kiểm chứng PII ngoài allowlist hiện tại, kể cả tên và public contacts,
  để đánh giá phần thiếu và chặn nhầm; không sửa fixture gốc của lab.
- Benchmark classifier/prompt cho bottleneck NeMo, giữ gate accuracy và privacy.
- Đo RAG/output/full request riêng trước khi quyết định budget production.
- Theo dõi drift bằng mẫu đã redact, giới hạn truy cập/thời gian lưu và gắn
  model/prompt version. Bộ 50/20/8/4 chưa đại diện traffic production.

## Bàn giao

Tasks 9a/9b/10/12 của Tâm và Task 11 của Quốc đạt đủ 12 tests offline.
Presidio thật đạt 12/12; smoke NeMo hiện hành đạt 13/13 gồm một input NeMo.
Chi tiết môi trường, hai lượt C và các phần chung còn thiếu nằm trong
`tam_guard_validation.md`. Blueprint đã có số guard/latency thật; metadata,
metric RAGAS và κ vẫn chờ A/B để nhóm hoàn thiện báo cáo chung.
