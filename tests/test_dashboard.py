import pandas as pd

from weather_pipeline.dashboard import generate_dashboard_dataset


def test_monthly_aggregation(tmp_path):
    processed = tmp_path / "processed"
    bi = tmp_path / "bi"
    processed.mkdir()
    frame = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        "city": ["bogota", "bogota"], "city_name": ["Bogotá", "Bogotá"],
        "department": ["Cundinamarca", "Cundinamarca"], "year": [2026, 2026], "month": [1, 1],
        "temperature_mean_c": [10.0, 20.0], "temperature_max_c": [15.0, 25.0],
        "temperature_min_c": [5.0, 10.0], "precipitation_sum_mm": [1.0, 2.0],
        "is_rainy_day": [True, True], "is_heavy_rain_day": [False, False],
        "is_strong_wind_day": [False, True], "is_adverse_day": [False, True],
        "wind_speed_max_kmh": [20.0, 40.0],
    })
    frame.to_parquet(processed / "part.parquet", index=False)
    parquet, csv = generate_dashboard_dataset(processed, bi, {"api": {"end_date": "2026-01-02"}, "storage": {"compression": "snappy"}})
    result = pd.read_parquet(parquet)
    assert result.loc[0, "temperature_mean_c"] == 15.0
    assert result.loc[0, "precipitation_total_mm"] == 3.0
    assert result.loc[0, "days_expected"] == 2
    assert csv.exists()
