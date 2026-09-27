from __future__ import annotations

from calendar import monthrange
from pathlib import Path

import pandas as pd


def generate_dashboard_dataset(processed_dir: Path, bi_dir: Path, pipeline: dict) -> tuple[Path, Path]:
    frame = pd.read_parquet(processed_dir)
    monthly = (
        frame.groupby(["city", "city_name", "department", "year", "month"], observed=True)
        .agg(
            days_observed=("date", "nunique"),
            temperature_mean_c=("temperature_mean_c", "mean"),
            temperature_max_c=("temperature_max_c", "max"),
            temperature_min_c=("temperature_min_c", "min"),
            precipitation_total_mm=("precipitation_sum_mm", "sum"),
            rainy_days=("is_rainy_day", "sum"),
            heavy_rain_days=("is_heavy_rain_day", "sum"),
            strong_wind_days=("is_strong_wind_day", "sum"),
            adverse_days=("is_adverse_day", "sum"),
            wind_speed_max_kmh=("wind_speed_max_kmh", "max"),
        )
        .reset_index()
    )
    end_date = pd.Timestamp(pipeline["api"]["end_date"])
    monthly["period"] = pd.to_datetime(dict(year=monthly["year"], month=monthly["month"], day=1))
    monthly["days_expected"] = monthly.apply(
        lambda row: end_date.day if row["year"] == end_date.year and row["month"] == end_date.month
        else monthrange(int(row["year"]), int(row["month"]))[1],
        axis=1,
    )
    monthly["coverage_pct"] = (monthly["days_observed"] / monthly["days_expected"] * 100).round(2)
    float_columns = ["temperature_mean_c", "temperature_max_c", "temperature_min_c", "precipitation_total_mm", "wind_speed_max_kmh"]
    monthly[float_columns] = monthly[float_columns].round(2)
    monthly = monthly.sort_values(["period", "city"]).reset_index(drop=True)
    bi_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = bi_dir / "weather_monthly.parquet"
    csv_path = bi_dir / "weather_monthly.csv"
    monthly.to_parquet(parquet_path, engine="pyarrow", compression=pipeline["storage"]["compression"], index=False)
    monthly.to_csv(csv_path, index=False, encoding="utf-8")
    return parquet_path, csv_path
