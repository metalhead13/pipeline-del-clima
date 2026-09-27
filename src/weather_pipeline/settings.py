from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Paths:
    root: Path
    raw: Path
    staging: Path
    processed: Path
    bi: Path
    quality: Path


def project_root() -> Path:
    configured = os.getenv("PROJECT_ROOT")
    if configured:
        return Path(configured).resolve()
    return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_settings() -> tuple[dict[str, Any], list[dict[str, Any]], Paths]:
    root = project_root()
    pipeline = load_yaml(root / "config" / "pipeline.yaml")
    cities = load_yaml(root / "config" / "cities.yaml")["cities"]
    paths = Paths(
        root=root,
        raw=root / "data" / "raw",
        staging=root / "data" / "staging",
        processed=root / "data" / "processed" / "weather_daily",
        bi=root / "data" / "bi",
        quality=root / "data" / "quality",
    )
    for path in (paths.raw, paths.staging, paths.processed, paths.bi, paths.quality):
        path.mkdir(parents=True, exist_ok=True)
    return pipeline, cities, paths
