# Bias Amplification Demo

Website demo phục vụ phân tích chủ đề **“Analyze Bias Amplification After Instruction Tuning”**.  
Mục tiêu của web là giúp người xem quan sát một cách trực quan việc instruction tuning có thể làm thay đổi các chỉ số bias như thế nào trên nhiều mô hình, nhiều instruction dataset, và nhiều benchmark khác nhau.

Web được xây dựng theo hướng:

- giao diện web thuần với `HTML + CSS + JavaScript`
- backend nhẹ bằng `Flask`
- đọc trực tiếp dữ liệu thực nghiệm từ các file `.csv` và `.json`
- có giữ phần **Test Lab** và **Custom Prompt Test** để người dùng tương tác

---

## 1. Mục tiêu của web

Web này không nhằm khẳng định rằng instruction tuning **luôn luôn** làm tăng bias.  
Thay vào đó, nó giúp trả lời các câu hỏi như:

- Sau instruction tuning, một model có đi xa hơn hay gần hơn so với mốc tham chiếu “ít bias hơn” không?
- Dataset tuning nào gây thay đổi mạnh hơn?
- Mức thay đổi đó có giống nhau trên StereoSet, WinoBias và BBQ không?
- Khi người dùng nhập prompt tự do, output của base model và tuned model khác nhau ra sao?

---

## 2. Các tab hiện có trên web

Sau khi tinh gọn theo đúng chủ đề chính, web hiện giữ lại các tab quan trọng nhất:

### Overview

Hiển thị bức tranh tổng quát của toàn bộ thí nghiệm:

- số lượng base model
- số lượng instruction dataset
- số lượng tuned runs
- số benchmark đang dùng
- một số key findings tóm tắt

### Dashboard

Dùng để nhìn toàn cục:

- heatmap amplification giữa `model × dataset`
- biểu đồ trung bình amplification theo model
- biểu đồ trung bình amplification theo dataset
- bảng kết quả đầy đủ

Tab này phù hợp để rút ra pattern tổng thể nhanh.

### Explorer

Dùng để soi chi tiết một cặp `model + dataset` cụ thể:

- điểm StereoSet SS
- điểm WinoBias
- điểm BBQ
- amplification theo từng benchmark
- amplification index tổng hợp
- phần diễn giải ngắn

### Test Lab

Đây là tab tương tác chính của web và gồm 2 phần:

#### Benchmark Test

Người dùng chọn:

- benchmark
- bias type
- test case
- model
- dataset

Sau đó web hiển thị:

- nội dung test case
- reference point
- baseline score
- tuned score
- amplification
- diễn giải kết quả

#### Custom Prompt Test

Người dùng nhập prompt tự do để so sánh định tính:

- output của base model
- output của tuned model

Lưu ý: phần này hiện được giới hạn về cấu hình nhẹ để đảm bảo chạy ổn định trên máy local.

### Ablation

Hiển thị **endpoint ablation**:

- step 0
- step 500

Tab này giúp quan sát sự thay đổi metric sau instruction tuning ở mức endpoint, không phải full learning curve.

### Methodology

Giải thích cách làm thí nghiệm:

- evaluate base model
- instruction tuning bằng LoRA
- evaluate tuned model
- tính bias amplification
- so sánh giữa các model và dataset

Tab này cũng chứa:

- công thức tính amplification
- benchmark reference points
- scope và caveats

---

## 3. Công nghệ sử dụng

### Frontend

- HTML
- CSS
- JavaScript
- Plotly.js

### Backend

- Flask

### Data / ML

- pandas
- numpy
- torch
- transformers
- peft
- accelerate
- sentencepiece

---

## 4. Cấu trúc thư mục chính

```text
bias-amplificationd-demo/
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── raw_results_v2_fixed_scoring.csv
│   ├── amplification_summary.csv
│   ├── ablation_kaggle_safe.csv
│   ├── benchmark_cases.csv
│   └── key_findings.json
│
├── static/
│   ├── css/
│   │   └── app.css
│   ├── images/
│   │   └── logo.png
│   ├── js/
│   │   └── app.js
│   └── vendor/
│       └── plotly.min.js
│
├── templates/
│   └── index.html
│
├── assets/
│   └── figures/
│
├── adapters/
│   └── ...
│
├── model_registry.json
└── utils/
    └── inference.py
```

---

## 5. Ý nghĩa của các file dữ liệu

### `data/amplification_summary.csv`

Đây là file quan trọng nhất cho phần dashboard và explorer.

Nó chứa các thông tin như:

- model
- dataset
- các score benchmark
- amplification theo từng benchmark
- amplification index tổng hợp

File này dùng để trả lời:

- model nào amplification mạnh nhất
- dataset nào gây thay đổi nhiều nhất
- hướng thay đổi bias là tăng hay giảm

### `data/raw_results_v2_fixed_scoring.csv`

Chứa score gốc và score sau tuning.  
Dùng chủ yếu để so sánh baseline và tuned result.

### `data/ablation_kaggle_safe.csv`

Dùng cho tab `Ablation`.  
Hiện dữ liệu là dạng endpoint:

- step 0
- step 500

### `data/benchmark_cases.csv`

Dùng cho `Benchmark Test` trong `Test Lab`.  
Giúp mô phỏng việc người dùng chọn một test case benchmark có sẵn mà không phải chạy benchmark gốc trực tiếp.

### `data/key_findings.json`

Chứa các key findings ngắn để hiển thị ở phần overview.

### `model_registry.json`

Chứa thông tin mapping giữa:

- base model
- dataset
- steps
- adapter path

File này rất quan trọng cho `Custom Prompt Test`.

### `adapters/`

Chứa các LoRA adapter đã train sẵn.  
Backend sẽ dùng các adapter này để nạp tuned model khi người dùng chạy live comparison.

---

## 6. Cách chạy project

### Khuyến nghị dùng Conda

Project hiện đang được thiết lập để chạy với environment:

```bash
nlpdemo
```

### Kích hoạt environment

```bash
conda activate nlpdemo
```

### Cài thư viện nếu chưa có

```bash
pip install -r requirements.txt
```

### Chạy web

```bash
python app.py
```

Sau đó mở trình duyệt tại:

```text
http://127.0.0.1:5000
```

Nếu giao diện chưa cập nhật sau khi sửa code, hãy dùng:

```text
Ctrl + F5
```

để hard refresh.

---

## 7. Hướng dẫn sử dụng nhanh

### Muốn xem tổng quan

Vào:

- `Overview`
- `Dashboard`

### Muốn phân tích chi tiết một model

Vào:

- `Explorer`

### Muốn cho người dùng thử benchmark case

Vào:

- `Test Lab` → `Benchmark Test`

### Muốn cho người dùng nhập prompt tự do

Vào:

- `Test Lab` → `Custom Prompt Test`

### Muốn xem thay đổi theo step

Vào:

- `Ablation`

### Muốn giải thích cách tính

Vào:

- `Methodology`

---

## 8. Lưu ý về Custom Prompt Test

Phần `Custom Prompt Test` là **định tính**, không phải kết quả benchmark chuẩn.

Nó chỉ nên được hiểu là:

- base model trả lời thế nào
- tuned model trả lời thế nào
- hai output có thay đổi về xu hướng hay không

Không nên dùng một prompt tự do duy nhất để kết luận định lượng về bias.

Ngoài ra:

- model lớn có thể ngốn RAM nhiều
- chạy local CPU có thể chậm
- vì lý do ổn định, cấu hình hiện tại ưu tiên setup nhẹ hơn

---

## 9. Ý nghĩa của “Bias Amplification”

Trong project này, amplification được hiểu là:

> sau instruction tuning, score của model đi xa hơn hay gần hơn so với mốc tham chiếu benchmark

Ví dụ reference points:

- StereoSet SS: `50`
- WinoBias: `50`
- BBQ: `33`

Công thức:

```text
|Tuned score - unbiased reference| - |Baseline score - unbiased reference|
```

Diễn giải:

- giá trị dương: model đi xa hơn khỏi mốc tham chiếu
- giá trị âm: model đi gần hơn mốc tham chiếu
- gần 0: thay đổi nhỏ

---

## 10. Những lưu ý quan trọng

- Web này là công cụ demo và trực quan hóa kết quả nghiên cứu.
- Nó không thay thế cho báo cáo học thuật đầy đủ.
- Kết quả phụ thuộc mạnh vào benchmark design, scoring method, dataset tuning, model size và training setup.
- `Ablation` hiện là endpoint ablation, chưa phải đường cong huấn luyện đầy đủ.

---

## 11. Gợi ý mở rộng trong tương lai

Nếu muốn nâng cấp thêm, có thể phát triển tiếp theo các hướng:

- bổ sung trang report/insight sâu hơn
- thêm export chart hoặc export report
- thêm lọc theo benchmark cụ thể trong dashboard
- hỗ trợ thêm model nhẹ khác cho live prompt test
- bổ sung so sánh nhiều model cùng lúc
- thêm phần giải thích định tính tự động cho output custom prompt

---

## 12. Liên hệ giữa web và notebook

Notebook `web-nlp.ipynb` là nơi sinh ra phần lớn dữ liệu đầu vào cho web.  
Nói cách khác:

- notebook tạo dữ liệu
- web đọc dữ liệu đó để hiển thị và cho người dùng tương tác

Nếu bạn thay đổi pipeline đánh giá trong notebook, hãy export lại các file dữ liệu tương ứng để web phản ánh kết quả mới.
