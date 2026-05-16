from pathlib import Path

import streamlit as st

from utils.data_loader import load_all_data
from utils.metrics import compute_overview_stats


st.title("Overview")
st.caption("Project: Bias Amplification After Instruction Tuning")

data = load_all_data(Path("."))
summary_df = data["summary"]
findings = data["findings"]
overview = compute_overview_stats(summary_df)

st.markdown(
    """
    This demo compares base models with their instruction-tuned variants across
    StereoSet, WinoBias, and BBQ. The core question is whether tuning moves each
    model closer to or further away from benchmark-specific reference points.
    """
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Base models", summary_df["model"].nunique())
c2.metric("Instruction datasets", summary_df["dataset"].nunique())
c3.metric("Tuned runs", len(summary_df))
c4.metric("Training setup", "LoRA, 500 steps")

st.subheader("Experiment Scope")
scope1, scope2, scope3 = st.columns(3)
scope1.markdown(
    """
    **Models**

    - distilgpt2
    - gpt2-medium
    - gpt2-large
    - facebook/opt-1.3b
    """
)
scope2.markdown(
    """
    **Instruction Datasets**

    - alpaca
    - dolly
    - oasst1
    """
)
scope3.markdown(
    """
    **Benchmarks**

    - StereoSet
    - WinoBias
    - BBQ
    """
)

st.subheader("Key Findings")
left, right = st.columns([1.2, 1])
with left:
    for item in findings["headline_findings"]:
        st.markdown(f"- {item}")
with right:
    worst = overview["highest_amplification_pair"]
    best = overview["lowest_amplification_pair"]
    st.metric(
        "Highest amplification pair",
        f'{worst["model"]} + {worst["dataset"]}',
        f'{worst["amplification_index"]:.2f}',
    )
    st.metric(
        "Strongest reduction pair",
        f'{best["model"]} + {best["dataset"]}',
        f'{best["amplification_index"]:.2f}',
    )

st.subheader("How To Read The Demo")
st.info(
    "Red indicates amplification above zero, teal indicates movement below zero, "
    "and near-gray values indicate small change."
)

st.subheader("Data Files")
st.code(
    "\n".join(
        [
            "data/amplification_summary.csv",
            "data/raw_results_v2_fixed_scoring.csv",
            "data/ablation_kaggle_safe.csv",
            "data/benchmark_cases.csv",
            "model_registry.json",
        ]
    )
)
