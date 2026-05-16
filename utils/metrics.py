from __future__ import annotations

import pandas as pd


REFERENCE_POINTS = {
    "stereoset_SS": 50.0,
    "winobias_score": 50.0,
    "bbq_bias_score": 33.0,
}

BENCHMARK_LABELS = {
    "stereoset_SS": "StereoSet SS",
    "winobias_score": "WinoBias",
    "bbq_bias_score": "BBQ",
}


def format_score(value: float) -> str:
    return f"{value:.2f}"


def describe_index(value: float) -> str:
    if value > 0.15:
        return "Instruction tuning amplified measured bias."
    if value < -0.15:
        return "Instruction tuning reduced measured bias."
    return "Instruction tuning produced little net change."


def classify_shift(value: float) -> str:
    if value > 0.15:
        return "Amplified"
    if value < -0.15:
        return "Reduced"
    return "Near-neutral"


def build_test_lab_record(raw_df: pd.DataFrame, summary_df: pd.DataFrame, model: str, dataset: str) -> dict:
    baseline = raw_df[(raw_df["model"] == model) & (raw_df["dataset"] == "baseline")].iloc[0]
    tuned = raw_df[(raw_df["model"] == model) & (raw_df["dataset"] == dataset)].iloc[0]
    summary_row = summary_df[(summary_df["model"] == model) & (summary_df["dataset"] == dataset)].iloc[0]
    return {
        "baseline": baseline,
        "tuned": tuned,
        "summary": summary_row,
    }


def compute_overview_stats(summary_df: pd.DataFrame) -> dict:
    worst = summary_df.sort_values("amplification_index", ascending=False).iloc[0]
    best = summary_df.sort_values("amplification_index", ascending=True).iloc[0]
    by_dataset = (
        summary_df.groupby("dataset", as_index=False)["amplification_index"]
        .mean()
        .sort_values("amplification_index", ascending=False)
    )
    return {
        "highest_amplification_pair": worst,
        "lowest_amplification_pair": best,
        "dataset_average": by_dataset,
    }


def melt_before_after(raw_df: pd.DataFrame, model: str) -> pd.DataFrame:
    subset = raw_df[raw_df["model"] == model].copy()
    metric_columns = ["stereoset_SS", "winobias_score", "bbq_bias_score"]
    melted = subset.melt(
        id_vars=["model", "dataset"],
        value_vars=metric_columns,
        var_name="metric",
        value_name="score",
    )
    return melted
