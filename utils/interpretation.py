from __future__ import annotations

from utils.metrics import classify_shift, describe_index


def interpret_model_dataset(row) -> str:
    direction = describe_index(float(row["amplification_index"]))
    ss = classify_shift(float(row["amp_SS"]))
    wino = classify_shift(float(row["amp_wino"]))
    bbq = classify_shift(float(row["amp_bbq"]))
    return (
        f"{direction} StereoSet: {ss}. "
        f"WinoBias: {wino}. "
        f"BBQ: {bbq}."
    )


def interpret_test_case(summary_row, benchmark: str) -> str:
    mapping = {
        "StereoSet": float(summary_row["amp_SS"]),
        "WinoBias": float(summary_row["amp_wino"]),
        "BBQ": float(summary_row["amp_bbq"]),
    }
    shift = mapping[benchmark]
    state = classify_shift(shift).lower()
    return (
        f"For this model-dataset pair, the selected benchmark moves in a {state} direction "
        f"relative to the baseline."
    )
