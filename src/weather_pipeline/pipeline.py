from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .dashboard import generate_dashboard_dataset
from .extract import extract_weather, latest_raw_files
from .settings import load_settings
from .storage import load_partitioned_parquet
from .transform import transform_weather
from .validation import validate_raw_data

LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def write_quality_report(path: Path, raw_report: dict | None = None, transformed_report: dict | None = None) -> Path:
    existing = {}
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
    report = {
        **existing,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        **({"raw_validation": raw_report} if raw_report else {}),
        **({"transformed_validation": transformed_report} if transformed_report else {}),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def stage_extract() -> list[Path]:
    pipeline, cities, paths = load_settings()
    return extract_weather(pipeline, cities, paths.raw)


def stage_validate_raw() -> dict:
    pipeline, cities, paths = load_settings()
    report = validate_raw_data(latest_raw_files(paths.raw, len(cities)), pipeline, cities)
    write_quality_report(paths.quality / "quality_report.json", raw_report=report)
    return report


def stage_transform() -> Path:
    pipeline, cities, paths = load_settings()
    output, report = transform_weather(latest_raw_files(paths.raw, len(cities)), pipeline, cities, paths.staging)
    write_quality_report(paths.quality / "quality_report.json", transformed_report=report)
    return output


def stage_load() -> Path:
    pipeline, _, paths = load_settings()
    return load_partitioned_parquet(paths.staging / "weather_daily.parquet", paths.processed, pipeline["storage"]["compression"])


def stage_dashboard() -> tuple[Path, Path]:
    pipeline, _, paths = load_settings()
    return generate_dashboard_dataset(paths.processed, paths.bi, pipeline)


def run_all() -> dict[str, object]:
    configure_logging()
    raw = stage_extract()
    raw_quality = stage_validate_raw()
    staging = stage_transform()
    processed = stage_load()
    bi = stage_dashboard()
    result = {"raw_files": [str(p) for p in raw], "raw_quality": raw_quality, "staging": str(staging), "processed": str(processed), "bi": [str(p) for p in bi]}
    LOGGER.info("Pipeline finalizado: %s", result)
    return result
