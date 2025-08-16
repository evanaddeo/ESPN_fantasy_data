from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd


REQUIRED_COLUMNS = ["rank", "name", "team", "pos"]


def ensure_columns(df: pd.DataFrame, *, include_bye: bool) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    cols = REQUIRED_COLUMNS + (["bye"] if include_bye and "bye" in df.columns else [])
    # Reorder to preferred layout when present
    available = [c for c in cols if c in df.columns]
    return df[available].copy()


def filter_positions(df: pd.DataFrame, positions: Optional[Iterable[str]]) -> pd.DataFrame:
    if not positions:
        return df
    allowed = [p.upper() for p in positions]
    return df[df["pos"].str.upper().isin(allowed)].copy()
