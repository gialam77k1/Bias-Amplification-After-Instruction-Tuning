from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLOR_SCALE = [
    [0.0, "#0f766e"],
    [0.5, "#e5e7eb"],
    [1.0, "#b91c1c"],
]


def plot_amplification_heatmap(summary_df: pd.DataFrame) -> go.Figure:
    pivot = summary_df.pivot(index="model", columns="dataset", values="amplification_index")
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=COLOR_SCALE,
        zmin=-1.5,
        zmax=1.5,
        text_auto=".2f",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        coloraxis_colorbar_title="Amp Index",
    )
    return fig


def plot_average_by_model(summary_df: pd.DataFrame) -> go.Figure:
    agg = summary_df.groupby("model", as_index=False)["amplification_index"].mean()
    fig = px.bar(
        agg,
        x="model",
        y="amplification_index",
        color="amplification_index",
        color_continuous_scale=COLOR_SCALE,
        title="Average Amplification by Model",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=48, b=10), coloraxis_showscale=False)
    return fig


def plot_average_by_dataset(summary_df: pd.DataFrame) -> go.Figure:
    agg = summary_df.groupby("dataset", as_index=False)["amplification_index"].mean()
    fig = px.bar(
        agg,
        x="dataset",
        y="amplification_index",
        color="amplification_index",
        color_continuous_scale=COLOR_SCALE,
        title="Average Amplification by Dataset",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=48, b=10), coloraxis_showscale=False)
    return fig


def plot_before_after(melted_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        melted_df,
        x="metric",
        y="score",
        color="dataset",
        barmode="group",
        title="Baseline vs Instruction-Tuned Scores",
        category_orders={"dataset": ["baseline", "alpaca", "dolly", "oasst1"]},
    )
    fig.update_layout(margin=dict(l=10, r=10, t=48, b=10))
    return fig


def plot_metric_deltas(summary_df: pd.DataFrame, model: str, dataset: str) -> go.Figure:
    row = summary_df[(summary_df["model"] == model) & (summary_df["dataset"] == dataset)].iloc[0]
    frame = pd.DataFrame(
        {
            "benchmark": ["StereoSet SS", "WinoBias", "BBQ"],
            "amplification": [row["amp_SS"], row["amp_wino"], row["amp_bbq"]],
        }
    )
    fig = px.bar(
        frame,
        x="benchmark",
        y="amplification",
        color="amplification",
        color_continuous_scale=COLOR_SCALE,
        title="Per-Benchmark Amplification",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=48, b=10), coloraxis_showscale=False)
    return fig


def plot_ablation(ablation_df: pd.DataFrame, model: str, dataset: str, metric: str) -> go.Figure:
    subset = ablation_df[(ablation_df["model"] == model) & (ablation_df["dataset"] == dataset)].copy()
    fig = px.line(
        subset,
        x="steps",
        y=metric,
        markers=True,
        title=f"Endpoint Ablation: {model} + {dataset}",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=48, b=10))
    return fig


def figure_path(name: str) -> Path:
    return Path("assets") / "figures" / name
