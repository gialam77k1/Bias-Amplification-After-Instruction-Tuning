# Bias Amplification Demo

Website demo cho chủ đề **Analyze Bias Amplification After Instruction Tuning**.

Web này giúp quan sát instruction tuning làm thay đổi các chỉ số bias như thế nào trên nhiều model và dataset, đồng thời cho phép người dùng:

- xem kết quả tổng quan qua dashboard
- soi chi tiết từng `model + dataset`
- thử `Benchmark Test` trong `Test Lab`
- nhập prompt tự do trong `Custom Prompt Test`
- xem endpoint ablation

## Các tab chính

- `Overview`: tóm tắt phạm vi thí nghiệm, số lượng model, dataset, benchmark và các key findings chính.
- `Dashboard`: hiển thị heatmap amplification, biểu đồ tổng hợp theo model/dataset và bảng kết quả đầy đủ.
- `Explorer`: cho phép chọn một cặp `model + dataset` để xem score, amplification và diễn giải ngắn.
- `Test Lab`: gồm `Benchmark Test` để xem case benchmark có sẵn và `Custom Prompt Test` để người dùng tự nhập prompt.
- `Ablation`: so sánh endpoint giữa step `0` và step `500` cho từng model và dataset.
- `Methodology`: giải thích cách tính amplification, reference points và các caveats cần lưu ý.

## Công nghệ sử dụng

- Frontend: `HTML`, `CSS`, `JavaScript`, `Plotly.js`
- Backend: `Flask`
- Xử lý dữ liệu / inference: `pandas`, `torch`, `transformers`, `peft`

## Dữ liệu đầu vào chính

Web đọc trực tiếp từ:

- `data/amplification_summary.csv`
- `data/raw_results_v2_fixed_scoring.csv`
- `data/ablation_kaggle_safe.csv`
- `data/benchmark_cases.csv`
- `data/key_findings.json`
- `model_registry.json`
- `adapters/`

## Cách chạy

Khuyến nghị dùng environment:

```bash
conda activate nlpdemo
```

Cài thư viện nếu cần:

```bash
pip install -r requirements.txt
```

Chạy web:

```bash
python app.py
```

Mở trình duyệt tại:

```text
http://127.0.0.1:5000
```

Nếu giao diện chưa cập nhật sau khi sửa code, dùng `Ctrl + F5`.

## Lưu ý

- `Custom Prompt Test` là so sánh **định tính**, không phải benchmark chuẩn.
- `Ablation` hiện là **endpoint ablation**, không phải full learning curve.
- Web không khẳng định instruction tuning luôn làm tăng bias; nó chỉ cho thấy model đi gần hơn hay xa hơn so với benchmark reference points.
