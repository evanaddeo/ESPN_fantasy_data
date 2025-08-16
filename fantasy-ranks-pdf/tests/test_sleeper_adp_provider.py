from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from fantasy_ranks.providers.sleeper_adp import SleeperADPProvider


class DummyResp:
    def __init__(self, data, status_code=200, headers=None):
        self._data = data
        self.status_code = status_code
        self.headers = headers or {"content-type": "application/json"}

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise RuntimeError("bad status")

    def json(self):
        return self._data


@pytest.mark.parametrize("lookback_hours", [168])
def test_sleeper_adp_trending(monkeypatch, lookback_hours):
    provider = SleeperADPProvider()

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get(self, url):
            if url.endswith("/state/nfl"):
                return DummyResp({"season": str(date.today().year)})
            if "trending/add" in url:
                return DummyResp([
                    {"player_id": "1111", "count": 123},
                    {"player_id": "2222", "count": 122},
                ])
            if url.endswith("/players/nfl"):
                return DummyResp({
                    "1111": {"first_name": "A", "last_name": "RB", "team": "AAA", "position": "RB"},
                    "2222": {"first_name": "B", "last_name": "WR", "team": "BBB", "position": "WR"},
                })
            raise AssertionError(f"unexpected URL {url}")

    import httpx

    monkeypatch.setattr(httpx, "Client", DummyClient)  # type: ignore[attr-defined]
    df = provider.fetch("ppr", limit=2)
    assert list(df.columns)[:4] == ["rank", "name", "team", "pos"]
    assert len(df) == 2
    assert df.iloc[0]["name"].startswith("A ")
