from __future__ import annotations

import argparse
import json

import duckdb

from .pipeline import (
    configure_logging,
    run_all,
    stage_dashboard,
    stage_extract,
    stage_load,
    stage_transform,
    stage_validate_raw,
)
from .settings import load_settings


def query_sample() -> list[tuple]:
    _, _, paths = load_settings()
    pattern = str(paths.processed / "**" / "*.parquet")
    return duckdb.sql(
        f"SELECT city, count(*) AS days, round(avg(temperature_mean_c), 2) AS avg_temp_c "
        f"FROM read_parquet('{pattern}', hive_partitioning=true) GROUP BY city ORDER BY city"
    ).fetchall()


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de datos históricos Open-Meteo")
    parser.add_argument("command", choices=["extract", "validate-raw", "transform", "load", "dashboard", "run", "query"])
    args = parser.parse_args()
    configure_logging()
    actions = {
        "extract": stage_extract,
        "validate-raw": stage_validate_raw,
        "transform": stage_transform,
        "load": stage_load,
        "dashboard": stage_dashboard,
        "run": run_all,
        "query": query_sample,
    }
    result = actions[args.command]()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
