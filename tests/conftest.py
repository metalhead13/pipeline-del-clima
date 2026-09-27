from __future__ import annotations

import pytest


@pytest.fixture
def thresholds():
    return {
        "rainy_day_mm": 1.0,
        "heavy_rain_mm": 20.0,
        "strong_wind_kmh": 39.0,
        "adverse_weather_codes": [65, 95, 96, 99],
    }


@pytest.fixture
def raw_document():
    return {
        "metadata": {
            "city": "bogota", "display_name": "Bogotá", "department": "Cundinamarca",
            "latitude": 4.711, "longitude": -74.0721, "timezone": "America/Bogota",
            "extracted_at": "2026-09-16T08:00:00-05:00",
        },
        "response": {"daily": {
            "time": ["2026-01-01", "2026-01-02"],
            "weather_code": [3, 95],
            "temperature_2m_mean": [14.0, 15.0],
            "temperature_2m_max": [20.0, 21.0],
            "temperature_2m_min": [8.0, 9.0],
            "precipitation_sum": [0.2, 25.0],
            "rain_sum": [0.2, 25.0],
            "precipitation_hours": [1.0, 8.0],
            "wind_speed_10m_max": [10.0, 45.0],
            "wind_gusts_10m_max": [20.0, 60.0],
        }},
    }
