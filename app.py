from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request
import pandas as pd

from utils.inference import list_available_pairs, run_comparison


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

app = Flask(__name__, template_folder="templates", static_folder="static")


def read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_summary() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "amplification_summary.csv")


def load_raw() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "raw_results_v2_fixed_scoring.csv")


def load_ablation() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "ablation_kaggle_safe.csv")


def load_cases() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "benchmark_cases.csv")


def sanitize_value(value):
    if pd.isna(value):
        return None
    return value


def sanitize_records(records: list[dict]) -> list[dict]:
    return [
        {key: sanitize_value(value) for key, value in record.items()}
        for record in records
    ]


def sanitize_dict(record: dict) -> dict:
    return {key: sanitize_value(value) for key, value in record.items()}


def build_bootstrap_payload() -> dict:
    summary_df = load_summary()
    raw_df = load_raw()
    ablation_df = load_ablation()
    cases_df = load_cases()
    findings = read_json(DATA_DIR / "key_findings.json")
    registry = read_json(BASE_DIR / "model_registry.json")

    highest = sanitize_dict(summary_df.sort_values("amplification_index", ascending=False).iloc[0].to_dict())
    lowest = sanitize_dict(summary_df.sort_values("amplification_index", ascending=True).iloc[0].to_dict())

    available_pairs = list_available_pairs(registry)
    available_live_pairs = {
        model: datasets
        for model, datasets in available_pairs.items()
        if model == "distilgpt2"
    }

    return {
        "summary": sanitize_records(summary_df.to_dict(orient="records")),
        "raw": sanitize_records(raw_df.to_dict(orient="records")),
        "ablation": sanitize_records(ablation_df.to_dict(orient="records")),
        "cases": sanitize_records(cases_df.to_dict(orient="records")),
        "findings": findings,
        "registry": registry,
        "available_pairs": available_pairs,
        "available_live_pairs": available_live_pairs,
        "overview": {
            "model_count": int(summary_df["model"].nunique()),
            "dataset_count": int(summary_df["dataset"].nunique()),
            "tuned_runs": int(len(summary_df)),
            "benchmark_count": 3,
            "highest_pair": highest,
            "lowest_pair": lowest,
        },
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/bootstrap")
def bootstrap():
    return jsonify(build_bootstrap_payload())


@app.post("/api/live-generate")
def live_generate():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    base_model = payload.get("base_model")
    dataset = payload.get("dataset")
    max_new_tokens = int(payload.get("max_new_tokens", 96))
    temperature = float(payload.get("temperature", 0.7))
    top_p = float(payload.get("top_p", 0.95))
    repetition_penalty = float(payload.get("repetition_penalty", 1.05))

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400
    if not base_model or not dataset:
        return jsonify({"error": "Base model and dataset are required."}), 400

    registry = read_json(BASE_DIR / "model_registry.json")

    try:
        result = run_comparison(
            registry=registry,
            base_model=base_model,
            dataset=dataset,
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
        )
    except Exception as exc:
        return (
            jsonify(
                {
                    "error": (
                        "Live inference failed. The base model may still need to be downloaded, "
                        "or the machine may not have enough memory for the selected model. "
                        "Please run the app from the nlpdemo environment."
                    ),
                    "details": str(exc),
                }
            ),
            500,
        )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, threaded=False)
