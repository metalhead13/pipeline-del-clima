import pandas as pd
import pytest

from weather_pipeline.validation import DataQualityError, validate_transformed


def settings():
    return {"api": {"start_date": "2026-01-01", "end_date": "2026-01-02"}}


def cities():
    return [{"city": "bogota"}]


def valid_frame():
    return pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        "city": ["bogota", "bogota"],
        "temperature_mean_c": [14.0, 15.0], "temperature_max_c": [20.0, 21.0],
        "temperature_min_c": [8.0, 9.0], "precipitation_sum_mm": [0.0, 2.0],
        "wind_speed_max_kmh": [10.0, 12.0], "weather_code": [1, 2],
    })


def test_valid_data_passes():
    report = validate_transformed(valid_frame(), settings(), cities())
    assert report["status"] == "PASS"
    assert report["actual_rows"] == 2


def test_duplicate_fails():
    frame = valid_frame()
    frame.loc[1, "date"] = frame.loc[0, "date"]
    with pytest.raises(DataQualityError):
        validate_transformed(frame, settings(), cities())
