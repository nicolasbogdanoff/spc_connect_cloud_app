from pathlib import Path

import pandas as pd
import pytest

import json

from app import build_audit_summary, normalize_data, perform_analysis, side_run_signals


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def sample_frame() -> pd.DataFrame:
    return pd.read_csv(REPOSITORY_ROOT / "sample_data.csv")


def test_sample_data_normalizes_to_four_measurements() -> None:
    normalized, measurement_columns = normalize_data(sample_frame())

    assert measurement_columns == ["x1", "x2", "x3", "x4"]
    assert normalized.shape == (20, 5)
    assert normalized["Subgrupo"].is_unique


def test_manual_exclusion_is_traceable_in_revised_analysis() -> None:
    normalized, measurement_columns = normalize_data(sample_frame())

    result = perform_analysis(
        normalized,
        measurement_columns,
        exclusion_mode="manual",
        manual_excluded="18",
        lsl=420.0,
        target=450.0,
        usl=480.0,
    )

    assert result["excluded"] == [18]
    assert 18 in result["revised_x_fail_all"]
    assert len(result["values"]) == 76
    assert result["cpk"] > 0


def test_invalid_specification_order_is_rejected() -> None:
    normalized, measurement_columns = normalize_data(sample_frame())

    with pytest.raises(ValueError, match="LSL < objetivo < USL"):
        perform_analysis(
            normalized,
            measurement_columns,
            exclusion_mode="manual",
            manual_excluded="",
            lsl=480.0,
            target=450.0,
            usl=420.0,
        )


def test_audit_summary_is_json_safe_and_preserves_traceability() -> None:
    normalized, measurement_columns = normalize_data(sample_frame())
    analysis = perform_analysis(
        normalized,
        measurement_columns,
        exclusion_mode="manual",
        manual_excluded="18",
        lsl=420.0,
        target=450.0,
        usl=480.0,
    )

    summary = build_audit_summary(analysis)
    json.dumps(summary)

    assert summary["method"] == "Xbar-R"
    assert summary["subgroups_total"] == 20
    assert summary["subgroups_used_for_revised_limits"] == 19
    assert summary["excluded_subgroups"] == [18]
    assert summary["specifications"] == {"lsl": 420.0, "target": 450.0, "usl": 480.0}


def test_side_run_signals_identifies_the_complete_run() -> None:
    stats = pd.DataFrame(
        {"Subgrupo": [1, 2, 3, 4, 5, 6], "Media": [10.0, 11.0, 12.0, 13.0, 14.0, 9.0]}
    )
    assert side_run_signals(stats, "Media", center=10.0, run_length=4) == [2, 3, 4, 5]


def test_side_run_signals_rejects_a_single_point_rule() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        side_run_signals(pd.DataFrame({"Subgrupo": [1], "Media": [1.0]}), "Media", 0, 1)
