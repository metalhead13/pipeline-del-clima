from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

LOGGER = logging.getLogger(__name__)


class ExtractionError(RuntimeError):
    pass


@retry(
    retry=retry_if_exception_type((requests.RequestException, ExtractionError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def _request_json(url: str, params: dict[str, Any], timeout: int) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise ExtractionError(payload.get("reason", "Open-Meteo devolvió error"))
    if "daily" not in payload or "time" not in payload["daily"]:
        raise ExtractionError("Respuesta sin bloque daily.time")
    return payload


def extract_weather(pipeline: dict[str, Any], cities: list[dict[str, Any]], raw_dir: Path) -> list[Path]:
    api = pipeline["api"]
    extraction_date = datetime.now(ZoneInfo(api["timezone"])).date().isoformat()
    output_files: list[Path] = []
    for city in cities:
        params = {
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "start_date": api["start_date"],
            "end_date": api["end_date"],
            "daily": ",".join(api["daily_variables"]),
            "timezone": api["timezone"],
        }
        LOGGER.info("Extrayendo Open-Meteo para %s", city["display_name"])
        payload = _request_json(api["base_url"], params, int(api["timeout_seconds"]))
        envelope = {
            "metadata": {
                **city,
                "requested_start_date": api["start_date"],
                "requested_end_date": api["end_date"],
                "timezone": api["timezone"],
                "extracted_at": datetime.now(ZoneInfo(api["timezone"])).isoformat(),
                "source": api["base_url"],
            },
            "response": payload,
        }
        folder = raw_dir / f"extraction_date={extraction_date}" / f"city={city['city']}"
        folder.mkdir(parents=True, exist_ok=True)
        output = folder / f"weather_{api['start_date']}_{api['end_date']}.json"
        output.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
        output_files.append(output)
        LOGGER.info("Raw guardado: %s", output)
    return output_files


def latest_raw_files(raw_dir: Path, expected_cities: int) -> list[Path]:
    batches = sorted((p for p in raw_dir.glob("extraction_date=*") if p.is_dir()), reverse=True)
    if not batches:
        raise FileNotFoundError("No hay lotes raw; ejecute extract primero")
    files = sorted(batches[0].glob("city=*/weather_*.json"))
    if len(files) != expected_cities:
        raise ExtractionError(f"Se esperaban {expected_cities} archivos raw y se encontraron {len(files)}")
    return files
