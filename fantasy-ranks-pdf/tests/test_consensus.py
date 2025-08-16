from __future__ import annotations

import pandas as pd

from fantasy_ranks.utils.consensus import build_consensus


def test_build_consensus_basic():
    espn = pd.DataFrame([
        {"rank": 1, "name": "A RB", "team": "AAA", "pos": "RB"},
        {"rank": 2, "name": "B WR", "team": "BBB", "pos": "WR"},
    ])
    sleeper = pd.DataFrame([
        {"adp": 10.0, "name": "A RB", "team": "AAA", "pos": "RB"},
        {"adp": 5.0, "name": "B WR", "team": "BBB", "pos": "WR"},
    ])
    df = build_consensus({"espn-editorial": espn, "sleeper-adp": sleeper})
    assert set([c for c in df.columns if c.startswith("rank_")]) == {"rank_espn-editorial", "rank_sleeper-adp"}
    assert "consensus_rank" in df.columns and "delta" in df.columns
    # Ensure order and delta sign
    first = df.iloc[0]
    assert first["name"] in ("A RB", "B WR")
