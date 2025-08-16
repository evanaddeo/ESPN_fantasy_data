from __future__ import annotations

from typing import Dict, Optional

import pandas as pd


def _rank_series(df: pd.DataFrame) -> pd.Series:
    if "consensus_rank" in df.columns:
        return df["consensus_rank"].astype(int)
    if "rank" in df.columns:
        return df["rank"].astype(int)
    return pd.Series(range(1, len(df) + 1))


def add_tiers(df: pd.DataFrame, *, method: str = "gap", gap_quantile: float = 0.9) -> pd.DataFrame:
    """Add a simple tier column using rank gap detection.

    method="gap": compute diffs on the chosen rank series; start a new tier when diff >= quantile.
    """
    if df.empty:
        df["tier"] = []
        return df
    sr = _rank_series(df)
    diffs = sr.diff().fillna(0)
    threshold = diffs.quantile(gap_quantile) if len(diffs) > 5 else (diffs.mean() + diffs.std())
    tier = 1
    tiers = []
    prev = sr.iloc[0]
    for d in diffs:
        if d >= threshold and d > 0:
            tier += 1
        tiers.append(tier)
    out = df.copy()
    out["tier"] = tiers
    return out


def add_vorp(
    df: pd.DataFrame,
    *,
    replacement_levels: Optional[Dict[str, int]] = None,
) -> pd.DataFrame:
    """Add VORP (value over replacement) per position using a simple inverse-rank proxy.

    For each position, let value = 1 / rank_within_position.
    Replacement level defaults: QB=12, RB=24, WR=24, TE=12, K=12, DST=12.
    VORP = value - (1 / replacement_level).
    """
    levels = {
        "QB": 12,
        "RB": 24,
        "WR": 24,
        "TE": 12,
        "K": 12,
        "DST": 12,
    }
    if replacement_levels:
        levels.update({k.upper(): v for k, v in replacement_levels.items()})

    out = df.copy()
    # Rank within position using consensus_rank if present else rank
    if "consensus_rank" in out.columns:
        out["_order"] = out["consensus_rank"].astype(int)
    elif "rank" in out.columns:
        out["_order"] = out["rank"].astype(int)
    else:
        out["_order"] = range(1, len(out) + 1)
    out["pos_rank"] = out.sort_values(["pos", "_order"]).groupby("pos").cumcount() + 1

    def compute_vorp(row: pd.Series) -> float:
        pos = str(row.get("pos", "")).upper()
        repl = levels.get(pos, 12)
        val = 1.0 / float(row["pos_rank"]) if float(row["pos_rank"]) > 0 else 0.0
        repl_val = 1.0 / float(repl)
        return round(val - repl_val, 4)

    out["VORP"] = out.apply(compute_vorp, axis=1)
    return out.drop(columns=["_order"], errors="ignore")


