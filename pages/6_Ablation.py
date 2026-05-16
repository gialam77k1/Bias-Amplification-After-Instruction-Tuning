from pathlib import Path

import streamlit as st

from utils.data_loader import load_all_data
from utils.plotting import plot_ablation


st.title("Ablation")
st.caption("Endpoint ablation only: step 0 versus step 500")

data = load_all_data(Path("."))
ablation_df = data["ablation"]

col1, col2, col3 = st.columns(3)
model = col1.selectbox("Model", sorted(ablation_df["model"].unique()))
dataset = col2.selectbox("Dataset", sorted(ablation_df["dataset"].unique()))
metric = col3.selectbox(
    "Metric",
    ["stereoset_SS", "winobias_score", "bbq_bias_score", "stereoset_ICAT"],
)

st.plotly_chart(plot_ablation(ablation_df, model, dataset, metric), use_container_width=True)

st.dataframe(
    ablation_df[(ablation_df["model"] == model) & (ablation_df["dataset"] == dataset)]
    .sort_values("steps")
    .reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)

st.info("This is endpoint ablation, not a full learning curve.")
