# Blueprint CI/CD cho RAG và guardrails

Nhóm: Dangcaps (theo tên repo). Cập nhật: 2026-10-12, Asia/Ho_Chi_Minh.
Kiến trúc, latency và tổng hợp: Nguyễn Trần Bảo Tâm — 2A202602408.
Phi phụ trách Monitoring; Quốc phụ trách CI gates; thông tin cá nhân của hai
thành viên do nhóm bổ sung trong TEAM.

Đây là đề xuất, chưa triển khai workflow production. Checkout chưa có artifacts
A/B/C, nên chưa có run timestamp hoặc model IDs thực chạy. Guard cấu hình là
`gpt-4o-mini` trong `guardrails/config.yml`, không phải bằng chứng đã gọi API.
Generation/evaluator/judge chờ metadata A/B; không suy evaluator từ judge.

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Đây là luồng tích hợp đề xuất; runner C kiểm tra stage riêng, chưa chạy RAG end-to-end.

Presidio analyze với ngôn ngữ en và recognizer VN; sau đó chỉ giữ VN_CCCD,
VN_PHONE, EMAIL_ADDRESS, PHONE_NUMBER. Allowlist giảm chặn nhầm thuật ngữ
policy bởi PERSON/LOCATION/DATE_TIME của NER tiếng Anh, nhưng không bao phủ
mọi loại PII. Yêu cầu lấy thông tin riêng của người khác còn do NeMo kiểm tra.
Có identifier thì chặn ngay, không gửi input gốc sang NeMo/RAG. Hàm trả bản
anonymized và entities/vị trí cho caller, không tự ghi log.

NeMo input đọc activated_rails[].stop, không dò cụm từ từ chối trong nội dung.
Chỉ input allowed mới đi tiếp vào RAG. Output rail do Quốc triển khai kiểm tra
answer có sẵn, giữ answer sạch hoặc thay bằng phản hồi của rail khi bị chặn.
Nếu engine/API lỗi, các hàm hiện truyền exception cho caller. Đề xuất service
bắt lỗi và fail closed với thông báo tạm thời không xử lý được, không trả
answer chưa kiểm tra hoặc fallback bỏ qua guard.

Key giữ trong `.env`/biến môi trường hoặc secret manager. Production log chỉ
giữ request ID, layer, loại entity, quyết định, latency và phiên bản cấu hình;
không log raw input, entities.text, context hay secrets. Rows của lab giữ input
gốc để đối chiếu fixture giả lập; không áp dụng cách lưu đó cho dữ liệu thật.

## Phạm vi và số đo latency

Task 12 đo input_layers_sequential: tạo engines trước đo, một event loop,
hai warm-up thực cho cả hai tầng rồi loại khỏi mẫu. Thu n_runs mẫu, cycle input,
luôn chạy Presidio và NeMo kể cả khi PII bị phát hiện. Dùng perf_counter, đơn vị
ms; input_guard_ms là tổng từng mẫu. Percentile linear tại (n-1)*q;
P95 tổng không phải tổng P95 hai tầng.

Chưa đo live: chưa có n_samples thực; thiết kế warmup_runs=2,
percentile_method=linear. Batch chính thức cần ít nhất 20 samples.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | chưa đo | chưa đo | chưa đo | Chờ runtime live |
| NeMo input | chưa đo | chưa đo | chưa đo | Chờ runtime live |
| Input guard sequential | chưa đo | chưa đo | chưa đo | Chờ guard_results.json |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài Task 12 |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài Task 12 |
| Full guard / request short-circuit | chưa đo | chưa đo | chưa đo | Đo riêng |

Target input layers: 500ms; latency_budget_ok chưa xác định. Chưa thể kết luận
bottleneck hoặc đạt budget. Sau batch C, chép số thật từ JSON kể cả khi vượt
target và so hai tầng để tìm phần chiếm thời gian chính. Đo bổ sung từng stage
RAG/output và toàn request bằng timer riêng, reuse engines, hai warm-up và ít
nhất 20 mẫu mỗi nhóm allowed/blocked; lưu timestamp/model/config/raw samples
và đường đi short-circuit. Không suy full guard từ input_guard_ms.

## CI gates đề xuất — Quốc hoàn thiện

Chạy unit tests offline cho PR và `python scripts/check_lab.py` khi có artifacts.
Nam chạy ba batch live chính thức, không chạy integration trùng lặp.
Đề xuất job đọc reports đã validate và trả exit code khác 0 khi faithfulness
<0.75, avg_score <0.65, attacks <18/20, clean không đạt 8/8 hoặc output sai.
Script quality gate này chưa triển khai; biến MIN_* không tự kiểm tra ngưỡng.
Ngưỡng lab bắt buộc vẫn 15/20. Full guard P95 <500ms chỉ áp dụng sau phép đo riêng.

## Monitoring và cải tiến — Phi hoàn thiện

Theo dõi attacks pass rate, clean FPR, output errors, latency từng tầng, API
errors, RAGAS theo distribution và Cohen’s κ. Đề xuất cảnh báo khi clean có
false positive, attacks dưới 18/20 hoặc input P95 vượt 500ms. Tâm xử lý
guard/latency, Phi phân tích RAGAS, Quốc phân tích judge/output, Nam điều phối
batch chạy lại và kiểm tra source hashes sau thay đổi.

Chưa có số thật cho RAGAS, κ, attacks hoặc FPR. Bộ 50/20/8/4 nhỏ, chưa đại diện
traffic production. Mẫu production cần redact, kiểm soát truy cập/thời gian lưu
và gắn model/prompt version để phát hiện drift. Cải tiến cần kiểm chứng: thử
allowlist trên toàn bộ clean; thử prompt trên attack khó cùng clean; thêm bộ
đánh giá độc lập sau lab; đo output overhead trước khi tối ưu full guard.
Không sửa fixture gốc hoặc dùng kết quả mock làm bằng chứng live.

## Bàn giao

Tasks 9a/9b/10/12 đạt 10 tests offline; 60 support tests đạt. Chờ Presidio/NeMo,
thử live nhỏ, Task 11 của Quốc và artifacts Nam chạy để hoàn tất số liệu.
Chưa sửa prompts vì chưa có bằng chứng live về false positive/attack lọt.
Đây là bản bàn giao có nội dung kiến trúc, chưa đủ bằng chứng để nộp cuối.
