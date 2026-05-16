from pathlib import Path

import streamlit as st

from utils.data_loader import load_all_data
from utils.interpretation import interpret_model_dataset
from utils.plotting import plot_metric_deltas


st.title("Model-Dataset Explorer")
st.caption("Inspect benchmark scores and amplification for a single pair")

data = load_all_data(Path("."))
summary_df = data["summary"]

models = sorted(summary_df["model"].unique())
datasets = sorted(summary_df["dataset"].unique())

c1, c2 = st.columns(2)
model = c1.selectbox("Model", models)
dataset = c2.selectbox("Instruction dataset", datasets)

row = summary_df[(summary_df["model"] == model) & (summary_df["dataset"] == dataset)].iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("StereoSet SS", f'{row["stereoset_SS"]:.2f}', f'{row["amp_SS"]:.2f}')
m2.metric("WinoBias", f'{row["winobias_score"]:.2f}', f'{row["amp_wino"]:.2f}')
m3.metric("BBQ", f'{row["bbq_bias_score"]:.2f}', f'{row["amp_bbq"]:.2f}')
m4.metric("Amplification Index", f'{row["amplification_index"]:.2f}')

st.plotly_chart(plot_metric_deltas(summary_df, model, dataset), use_container_width=True)

st.subheader("Interpretation")
st.success(interpret_model_dataset(row))

st.subheader("Detailed Record")
st.json(
    {
        "model": row["model"],
        "dataset": row["dataset"],
        "stereoset_SS": float(row["stereoset_SS"]),
        "winobias_score": float(row["winobias_score"]),
        "bbq_bias_score": float(row["bbq_bias_score"]),
        "amp_SS": float(row["amp_SS"]),
        "amp_wino": float(row["amp_wino"]),
        "amp_bbq": float(row["amp_bbq"]),
        "amplification_index": float(row["amplification_index"]),
    },
    expanded=True,
)
