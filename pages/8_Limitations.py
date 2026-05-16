import streamlit as st


st.title("Limitations")
st.caption("Scope and caveats")

st.markdown(
    """
    - The demo does not claim that instruction tuning always increases bias.
    - It only measures whether each model-dataset pair moves closer to or further away from benchmark-specific reference points.
    - The results depend on model size, dataset choice, benchmark design, scoring method, and training steps.
    - The current MVP focuses on CSV-backed analysis, not live generation quality or causal attribution.
    - Endpoint ablation should not be interpreted as a full training trajectory.
    """
)

st.warning(
    "Benchmark scores are useful but incomplete. They should be read as one layer of evidence, "
    "not as a universal statement about model behavior in every deployment setting."
)
