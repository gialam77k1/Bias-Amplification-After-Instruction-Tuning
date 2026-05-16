from pathlib import Path

import streamlit as st

from utils.data_loader import load_all_data
from utils.plotting import (
    plot_amplification_heatmap,
    plot_average_by_dataset,
    plot_average_by_model,
)


st.title("Dashboard")
st.caption("Model × dataset view of measured bias amplification")

data = load_all_data(Path("."))
summary_df = data["summary"]

st.plotly_chart(plot_amplification_heatmap(summary_df), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_average_by_model(summary_df), use_container_width=True)
with col2:
    st.plotly_chart(plot_average_by_dataset(summary_df), use_container_width=True)

st.subheader("Full Results")
st.dataframe(
    summary_df.sort_values(["model", "dataset"]).reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)
