from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


class DataQualityError(ValueError):
    pass


def validate_raw_data(files: list[Path], pipeline: dict[str, Any], cities: list[dict[str, Any]]) -> dict[str, Any]:
    api = pipeline["api"]
    expected_dates = pd.date_range(api["start_date"], api["end_date"], freq="D").strftime("%Y-%m-%d").tolist()
    expected_city_ids = {c["city"] for c in cities}
    found: set[str] = set()
    details = []
    errors = []
    for file in files:
        doc = json.loads(file.read_text(encoding="utf-8"))
        metadata, response = doc.get("metadata", {}), doc.get("response", {})
        city = metadata.get("city")
        found.add(city)
        daily = response.get("daily", {})
        dates = daily.get("time", [])
        lengths = {key: len(value) for key, value in daily.items() if isinstance(value, list)}
        consistent = bool(lengths) and len(set(lengths.values())) == 1
        exact_range = dates == expected_dates
        if not consistent:
            errors.append(f"{city}: arrays daily con longitudes diferentes")
        if not exact_range:
            errors.append(f"{city}: rango diario incompleto o desordenado")
        details.append({"city": city, "rows": len(dates), "consistent_arrays": consistent, "exact_range": exact_range})
    if found != expected_city_ids:
        errors.append(f"Ciudades encontradas {sorted(found)} != esperadas {sorted(expected_city_ids)}")
    report = {"status": "PASS" if not errors else "FAIL", "files": len(files), "details": details, "errors": errors}
    if errors:
        raise DataQualityError("; ".join(errors))
    return report


def validate_transformed(df: pd.DataFrame, pipeline: dict[str, Any], cities: list[dict[str, Any]]) -> dict[str, Any]:
    api = pipeline["api"]
    expected_dates = pd.date_range(api["start_date"], api["end_date"], freq="D")
    expected_rows = len(expected_dates) * len(cities)
    duplicate_rows = int(df.duplicated(["city", "date"]).sum())
    required = [
        "temperature_mean_c", "temperature_max_c", "temperature_min_c",
        "precipitation_sum_mm", "wind_speed_max_kmh", "weather_code",
    ]
    nulls = {column: int(df[column].isna().sum()) for column in required}
    out_of_range = int(((df["date"] < expected_dates.min()) | (df["date"] > expected_dates.max())).sum())
    missing_dates: dict[str, list[str]] = {}
    for city in (c["city"] for c in cities):
        actual = set(df.loc[df["city"] == city, "date"])
        missing_dates[city] = [d.strftime("%Y-%m-%d") for d in expected_dates if d not in actual]
    errors = []
    if len(df) != expected_rows:
        errors.append(f"Filas: {len(df)}; esperadas: {expected_rows}")
    if duplicate_rows:
        errors.append(f"Duplicados city/date: {duplicate_rows}")
    if out_of_range:
        errors.append(f"Fechas fuera de rango: {out_of_range}")
    if any(nulls.values()):
        errors.append(f"Nulos en campos obligatorios: {nulls}")
    if any(missing_dates.values()):
        errors.append("Existen fechas faltantes")
    report = {
        "status": "PASS" if not errors else "FAIL",
        "expected_rows": expected_rows,
        "actual_rows": int(len(df)),
        "duplicate_city_date_rows": duplicate_rows,
        "out_of_range_rows": out_of_range,
        "null_counts": nulls,
        "missing_dates": missing_dates,
        "rows_by_city": {str(k): int(v) for k, v in df.groupby("city").size().items()},
        "errors": errors,
    }
    if errors:
        raise DataQualityError("; ".join(errors))
    return report
