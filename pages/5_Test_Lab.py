from pathlib import Path

import streamlit as st

from utils.data_loader import load_all_data
from utils.interpretation import interpret_test_case
from utils.metrics import build_test_lab_record
from utils.model_runner import list_available_pairs, run_comparison


st.title("Test Lab")
st.caption("Lightweight benchmark case inspection without live model inference")

data = load_all_data(Path("."))
raw_df = data["raw"]
summary_df = data["summary"]
cases_df = data["cases"]

tab_a, tab_b = st.tabs(["Benchmark Test", "Custom Prompt Test"])

with tab_a:
    benchmarks = sorted(cases_df["benchmark"].unique())
    benchmark = st.selectbox("Benchmark", benchmarks)

    filtered_cases = cases_df[cases_df["benchmark"] == benchmark]
    bias_type = st.selectbox("Bias type", sorted(filtered_cases["bias_type"].unique()))
    filtered_cases = filtered_cases[filtered_cases["bias_type"] == bias_type]
    case_label = st.selectbox(
        "Test case",
        filtered_cases["case_title"].tolist(),
    )
    case_row = filtered_cases[filtered_cases["case_title"] == case_label].iloc[0]

    model = st.selectbox("Model", sorted(summary_df["model"].unique()), key="lab_model")
    dataset = st.selectbox("Instruction dataset", sorted(summary_df["dataset"].unique()), key="lab_dataset")

    record = build_test_lab_record(raw_df, summary_df, model, dataset)

    st.subheader("Selected Test Case")
    st.markdown(f"**Context**: {case_row['context']}")
    st.markdown(f"**Option A**: {case_row['option_a']}")
    st.markdown(f"**Option B**: {case_row['option_b']}")
    if str(case_row["option_c"]).strip():
        st.markdown(f"**Option C**: {case_row['option_c']}")

    baseline_key = {
        "StereoSet": "stereoset_SS",
        "WinoBias": "winobias_score",
        "BBQ": "bbq_bias_score",
    }[benchmark]

    tuned_key = baseline_key
    amplification_key = {
        "StereoSet": "amp_SS",
        "WinoBias": "amp_wino",
        "BBQ": "amp_bbq",
    }[benchmark]

    c1, c2, c3 = st.columns(3)
    c1.metric("Baseline score", f'{record["baseline"][baseline_key]:.2f}')
    c2.metric("Tuned score", f'{record["tuned"][tuned_key]:.2f}')
    c3.metric("Amplification", f'{record["summary"][amplification_key]:.2f}')

    st.subheader("Interpretation")
    st.info(interpret_test_case(record["summary"], benchmark))

    st.caption(
        "This tab reuses benchmark-style cases for explanation only. Quantitative conclusions "
        "should still be grounded in the full benchmark evaluation."
    )

with tab_b:
    registry = data["registry"]
    pair_map = list_available_pairs(registry)

    st.warning(
        "This test is qualitative only. Use the benchmark-backed pages for quantitative conclusions."
    )
    st.caption(
        "The first run may be slow because the base Hugging Face model may need to be loaded or downloaded."
    )

    live_models = sorted(pair_map.keys())
    selected_model = st.selectbox("Base model", live_models, key="custom_model")
    selected_dataset = st.selectbox(
        "Tuned dataset",
        pair_map[selected_model],
        key="custom_dataset",
    )

    prompt = st.text_area(
        "Custom prompt",
        value="A doctor is usually a ",
        height=160,
        key="custom_prompt",
        placeholder="Type any prompt you want to compare across base and tuned models.",
    )

    s1, s2, s3 = st.columns(3)
    max_new_tokens = s1.slider("Max new tokens", 16, 256, 96, 8)
    temperature = s2.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
    top_p = s3.slider("Top-p", 0.1, 1.0, 0.95, 0.05)
    repetition_penalty = st.slider("Repetition penalty", 1.0, 1.5, 1.05, 0.05)

    if st.button("Run live comparison", type="primary"):
        with st.spinner("Loading base model, adapter, and generating outputs..."):
            try:
                result = run_comparison(
                    registry=registry,
                    base_model=selected_model,
                    dataset=selected_dataset,
                    prompt=prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    repetition_penalty=repetition_penalty,
                )
            except Exception as exc:
                st.error(
                    "Live inference could not complete. This usually means the base model weights "
                    "are not cached yet, the download failed, or the machine ran out of memory."
                )
                st.exception(exc)
            else:
                lcol, rcol = st.columns(2)
                with lcol:
                    st.subheader("Base model output")
                    st.code(result["base_output"] or "[No text generated]", language="text")
                with rcol:
                    st.subheader("Tuned model output")
                    st.code(result["tuned_output"] or "[No text generated]", language="text")

                st.subheader("Run metadata")
                st.json(
                    {
                        "base_model": selected_model,
                        "dataset": selected_dataset,
                        "adapter_id": result["adapter_id"],
                        "adapter_path": result["adapter_path"],
                        "benchmark_scores": result["scores"],
                        "benchmark_deltas": result["delta"],
                    },
                    expanded=False,
                )
