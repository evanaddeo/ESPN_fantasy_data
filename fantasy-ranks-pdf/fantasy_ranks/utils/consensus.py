from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd


ProviderName = str


def _prepare_provider_df(df: pd.DataFrame, provider: ProviderName) -> pd.DataFrame:
    out = df.copy()
    # Ensure required columns exist
    for col in ["name", "team", "pos"]:
        if col not in out.columns:
            out[col] = ""
    # Normalize rank field
    if "rank" in out.columns and pd.api.types.is_numeric_dtype(out["rank"]):
        out["_rank"] = out["rank"].astype(int)
    elif "adp" in out.columns:
        # Convert ADP to rank by sorting ascending
        out["_rank"] = (out["adp"].rank(method="first", ascending=True)).astype(int)
    else:
        # Fallback: current order
        out["_rank"] = range(1, len(out) + 1)
    # Canonical join key
    out["_key"] = (
        out["name"].astype(str).str.strip().str.lower()
        + "|"
        + out["pos"].astype(str).str.strip().str.upper()
    )
    # Provider-specific columns to keep
    return out[["_key", "name", "team", "pos", "_rank"]].rename(columns={"_rank": f"rank_{provider}"})


def build_consensus(providers: Dict[ProviderName, pd.DataFrame]) -> pd.DataFrame:
    """Build consensus ranking across providers.

    Returns columns: name, team, pos, rank_<provider>, delta, consensus_rank
    Delta is defined only for the pair ESPN vs Sleeper if both present; else 0.
    Consensus rank is the mean of available provider ranks, then re-ranked (1..N).
    """
    prepared: List[pd.DataFrame] = []
    for pname, df in providers.items():
        prepared.append(_prepare_provider_df(df, pname))

    # Merge on _key
    merged = prepared[0]
    for part in prepared[1:]:
        merged = pd.merge(merged, part, on=["_key", "name", "team", "pos"], how="outer")

    # Compute consensus mean rank across available provider rank columns
    rank_cols = [c for c in merged.columns if c.startswith("rank_")]
    merged["consensus_mean"] = merged[rank_cols].mean(axis=1, skipna=True)
    # Assign consensus rank (1..N) by ordering mean
    merged = merged.sort_values(["consensus_mean", "name"]).reset_index(drop=True)
    merged["consensus_rank"] = range(1, len(merged) + 1)

    # Delta: ESPN vs Sleeper if present
    espn_col = next((c for c in rank_cols if c == "rank_espn-editorial" or c == "rank_ESPN"), None)
    sleeper_col = next((c for c in rank_cols if c == "rank_sleeper-adp" or c == "rank_Sleeper"), None)
    if espn_col and sleeper_col:
        merged["delta"] = merged[espn_col] - merged[sleeper_col]
    else:
        merged["delta"] = 0

    # Final columns
    keep_cols = [
        "name",
        "team",
        "pos",
    ] + rank_cols + ["delta", "consensus_rank"]

    return merged[keep_cols].reset_index(drop=True)
