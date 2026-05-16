import streamlit as st


st.title("Methodology")
st.caption("How the experiment is structured")

st.markdown(
    """
    ```text
    Base model
      ↓
    Evaluate on bias benchmarks
      ↓
    Instruction tuning with LoRA
      ↓
    Evaluate tuned model
      ↓
    Compute amplification
      ↓
    Compare across models and datasets
    ```
    """
)

st.subheader("Amplification Formula")
st.latex(
    r"""
    \mathrm{Bias\ Amplification}
    =
    \left| \mathrm{Tuned\ score} - \mathrm{reference} \right|
    -
    \left| \mathrm{Baseline\ score} - \mathrm{reference} \right|
    """
)

st.subheader("Reference Points")
st.markdown(
    """
    - StereoSet SS: 50
    - WinoBias: 50
    - BBQ: 33
    """
)

st.subheader("Interpretation Rule")
st.markdown(
    """
    - Positive amplification means the tuned model moved further away from the reference point.
    - Negative amplification means the tuned model moved closer to the reference point.
    - Near-zero amplification means little measured change.
    """
)
