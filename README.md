# Bias Amplification Demo

Flask web demo for analyzing bias amplification after instruction tuning across multiple base models, instruction datasets, and bias benchmarks.

## Features

- Overview of experiment scope and key findings
- Dashboard for amplification heatmaps and aggregate comparisons
- Model-dataset explorer with automatic interpretation
- Before vs After comparison against baseline
- Benchmark Test Lab backed by benchmark cases
- Live custom prompt testing with base vs tuned generation
- Endpoint ablation analysis
- Methodology and limitations pages

## Project Structure

```text
bias-amplificationd-demo/
├── app.py
├── requirements.txt
├── README.md
├── data/
├── assets/
├── pages/
└── utils/
```

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

## Data Inputs

The web app reads directly from:

- `data/raw_results_v2_fixed_scoring.csv`
- `data/amplification_summary.csv`
- `data/ablation_kaggle_safe.csv`
- `data/benchmark_cases.csv`
- `data/key_findings.json`

## Live Prompt Test

The custom prompt tab can load a base model plus a matching LoRA adapter from `adapters/`.
The first run may take time because Hugging Face base model weights may need to be downloaded and cached locally.
