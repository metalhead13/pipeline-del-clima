from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .validation import validate_transformed

COLUMN_MAP = {
    "time": "date",
    "weather_code": "weather_code",
    "temperature_2m_mean": "temperature_mean_c",
    "temperature_2m_max": "temperature_max_c",
    "temperature_2m_min": "temperature_min_c",
    "precipitation_sum": "precipitation_sum_mm",
    "rain_sum": "rain_sum_mm",
    "precipitation_hours": "precipitation_hours",
    "wind_speed_10m_max": "wind_speed_max_kmh",
    "wind_gusts_10m_max": "wind_gusts_max_kmh",
}


def raw_document_to_frame(document: dict, thresholds: dict) -> pd.DataFrame:
    metadata = document["metadata"]
    daily = document["response"]["daily"]
    frame = pd.DataFrame(daily).rename(columns=COLUMN_MAP)
    frame["date"] = pd.to_datetime(frame["date"])
    numeric = [column for column in COLUMN_MAP.values() if column != "date"]
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["city"] = metadata["city"]
    frame["city_name"] = metadata["display_name"]
    frame["department"] = metadata["department"]
    frame["latitude"] = float(metadata["latitude"])
    frame["longitude"] = float(metadata["longitude"])
    frame["timezone"] = metadata["timezone"]
    frame["source_extracted_at"] = pd.to_datetime(metadata["extracted_at"])
    frame["year"] = frame["date"].dt.year.astype("int16")
    frame["month"] = frame["date"].dt.month.astype("int8")
    frame["temperature_range_c"] = frame["temperature_max_c"] - frame["temperature_min_c"]
    frame["is_rainy_day"] = frame["precipitation_sum_mm"] >= float(thresholds["rainy_day_mm"])
    frame["is_heavy_rain_day"] = frame["precipitation_sum_mm"] >= float(thresholds["heavy_rain_mm"])
    frame["is_strong_wind_day"] = frame["wind_speed_max_kmh"] >= float(thresholds["strong_wind_kmh"])
    severe_codes = set(thresholds["adverse_weather_codes"])
    frame["is_adverse_day"] = (
        frame["is_heavy_rain_day"]
        | frame["is_strong_wind_day"]
        | frame["weather_code"].isin(severe_codes)
    )
    columns = [
        "date", "city", "city_name", "department", "latitude", "longitude", "timezone",
        "year", "month", "weather_code", "temperature_mean_c", "temperature_max_c",
        "temperature_min_c", "temperature_range_c", "precipitation_sum_mm", "rain_sum_mm",
        "precipitation_hours", "wind_speed_max_kmh", "wind_gusts_max_kmh", "is_rainy_day",
        "is_heavy_rain_day", "is_strong_wind_day", "is_adverse_day", "source_extracted_at",
    ]
    return frame[columns]


def transform_weather(files: list[Path], pipeline: dict, cities: list[dict], staging_dir: Path) -> tuple[Path, dict]:
    frames = [raw_document_to_frame(json.loads(path.read_text(encoding="utf-8")), pipeline["thresholds"]) for path in files]
    result = pd.concat(frames, ignore_index=True).sort_values(["city", "date"]).reset_index(drop=True)
    report = validate_transformed(result, pipeline, cities)
    output = staging_dir / "weather_daily.parquet"
    result.to_parquet(output, engine="pyarrow", compression=pipeline["storage"]["compression"], index=False)
    return output, report
