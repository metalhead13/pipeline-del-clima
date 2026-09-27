from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


def load_partitioned_parquet(staging_file: Path, target_dir: Path, compression: str) -> Path:
    frame = pd.read_parquet(staging_file)
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(
        target_dir,
        engine="pyarrow",
        compression=compression,
        index=False,
        partition_cols=["city", "year", "month"],
    )
    return target_dir
