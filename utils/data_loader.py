from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = "data"


@st.cache_data(show_spinner=False)
def load_summary(base_path: Path) -> pd.DataFrame:
    return pd.read_csv(base_path / DATA_DIR / "amplification_summary.csv")


@st.cache_data(show_spinner=False)
def load_raw_results(base_path: Path) -> pd.DataFrame:
    return pd.read_csv(base_path / DATA_DIR / "raw_results_v2_fixed_scoring.csv")


@st.cache_data(show_spinner=False)
def load_ablation(base_path: Path) -> pd.DataFrame:
    return pd.read_csv(base_path / DATA_DIR / "ablation_kaggle_safe.csv")


@st.cache_data(show_spinner=False)
def load_benchmark_cases(base_path: Path) -> pd.DataFrame:
    return pd.read_csv(base_path / DATA_DIR / "benchmark_cases.csv")


@st.cache_data(show_spinner=False)
def load_key_findings(base_path: Path) -> dict:
    with open(base_path / DATA_DIR / "key_findings.json", "r", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data(show_spinner=False)
def load_model_registry(base_path: Path) -> dict:
    registry_path = base_path / "model_registry.json"
    if not registry_path.exists():
        return {"adapters": []}

    with open(registry_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_all_data(base_path: Path) -> dict:
    return {
        "summary": load_summary(base_path),
        "raw": load_raw_results(base_path),
        "ablation": load_ablation(base_path),
        "cases": load_benchmark_cases(base_path),
        "findings": load_key_findings(base_path),
        "registry": load_model_registry(base_path),
    }
