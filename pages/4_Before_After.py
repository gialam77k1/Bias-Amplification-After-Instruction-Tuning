from pathlib import Path

import streamlit as st

from utils.data_loader import load_all_data
from utils.metrics import melt_before_after
from utils.plotting import plot_before_after


st.title("Before vs After")
st.caption("Baseline comparison is central to the amplification claim")

data = load_all_data(Path("."))
raw_df = data["raw"]

model = st.selectbox("Select model", sorted(raw_df["model"].unique()))
melted = melt_before_after(raw_df, model)

st.plotly_chart(plot_before_after(melted), use_container_width=True)

baseline = raw_df[(raw_df["model"] == model) & (raw_df["dataset"] == "baseline")].iloc[0]
baseline_cols = st.columns(3)
baseline_cols[0].metric("Baseline StereoSet SS", f'{baseline["stereoset_SS"]:.2f}')
baseline_cols[1].metric("Baseline WinoBias", f'{baseline["winobias_score"]:.2f}')
baseline_cols[2].metric("Baseline BBQ", f'{baseline["bbq_bias_score"]:.2f}')

st.subheader("Comparison Table")
st.dataframe(
    raw_df[raw_df["model"] == model].sort_values("dataset"),
    use_container_width=True,
    hide_index=True,
)

st.info(
    "This page emphasizes change relative to the untuned baseline, rather than treating "
    "post-tuning scores in isolation."
)
