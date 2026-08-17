from pathlib import Path

import pandas as pd
import pytest

from app import normalize_data, perform_analysis


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
