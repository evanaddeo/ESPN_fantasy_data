from __future__ import annotations

import os
from datetime import date
from typing import Iterable, Optional

import httpx
import pandas as pd

from fantasy_ranks.models import Scoring
from fantasy_ranks.providers.base import Provider
from fantasy_ranks.utils.caching import cache_get, cache_put, DEFAULT_TTL_SECONDS


SLEEPER_BASE = "https://api.sleeper.app/v1"


class SleeperADPProvider(Provider):
    name = "sleeper-adp"
    homepage_url = "https://sleeper.com/"

    def fetch(
        self,
        scoring: Scoring,
        *,
        positions: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
        season: Optional[int] = None,
    ) -> pd.DataFrame:
        # TTL default 6h
        ttl_seconds = int(os.getenv("SLEEPER_CACHE_TTL_SECONDS", str(21600)))

        season = season or self._get_season(ttl_seconds=ttl_seconds)
        cache_key = f"v1::sleeper-adp::{season}::{scoring}"
        cached = cache_get(cache_key, ttl_seconds=ttl_seconds)
        if cached is not None:
            df = pd.DataFrame(cached)
            return self._finalize(df, positions=positions, limit=limit)

        # Preferred: official ADP (if available in future). Fallback: env-provided ADP URL.
        fallback_url = os.getenv("SLEEPER_ADP_FALLBACK_URL")
        if fallback_url:
            df = self._fetch_fallback_adp(fallback_url)
        else:
            # Last resort: approximate ranking order via trending adds.
            df = self._fetch_trending_adp()

        df["source"] = self.name
        df["scoring"] = scoring
        df["date"] = date.today().isoformat()
        cache_put(cache_key, df.to_dict(orient="records"))
        return self._finalize(df, positions=positions, limit=limit)

    def _get_season(self, *, ttl_seconds: int) -> int:
        cache_key = "sleeper-state-nfl"
        cached = cache_get(cache_key, ttl_seconds=ttl_seconds)
        if cached and isinstance(cached, dict) and "season" in cached:
            try:
                return int(cached["season"])
            except Exception:
                pass
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            resp = client.get(f"{SLEEPER_BASE}/state/nfl")
            resp.raise_for_status()
            data = resp.json()
            cache_put(cache_key, data)
            return int(data.get("season") or date.today().year)

    def _fetch_trending_adp(self) -> pd.DataFrame:
        # Get trending adds and player map; rank by count desc
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            trend = client.get(f"{SLEEPER_BASE}/players/nfl/trending/add?lookback_hours=168&limit=300")
            trend.raise_for_status()
            trending = trend.json()
            players_resp = client.get(f"{SLEEPER_BASE}/players/nfl")
            players_resp.raise_for_status()
            players = players_resp.json()

        rows = []
        for idx, item in enumerate(trending, start=1):
            pid = str(item.get("player_id"))
            meta = players.get(pid, {})
            name = f"{meta.get('first_name','').strip()} {meta.get('last_name','').strip()}".strip()
            team = (meta.get("team") or "").upper()
            pos = (meta.get("position") or (meta.get("fantasy_positions") or [""])[0]).upper()
            if pos == "D/ST" or pos == "DST":
                pos = "DST"
            rows.append({
                "rank": idx,
                "name": name or pid,
                "team": team,
                "pos": pos,
                "bye": None,
                "adp": None,
            })
        return pd.DataFrame(rows, columns=["rank", "name", "team", "pos", "bye", "adp"]).sort_values("rank")

    def _fetch_fallback_adp(self, url: str) -> pd.DataFrame:
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
        rows = []
        # Expect a list of entries with name/team/position/adp
        for idx, item in enumerate(data, start=1):
            name = str(item.get("name", "")).strip()
            team = str(item.get("team", "")).upper()
            pos = str(item.get("position", "")).upper()
            adp = item.get("adp")
            rows.append({
                "rank": idx,
                "name": name,
                "team": team,
                "pos": pos,
                "bye": None,
                "adp": adp,
            })
        return pd.DataFrame(rows, columns=["rank", "name", "team", "pos", "bye", "adp"]).sort_values("rank")

    def _finalize(self, df: pd.DataFrame, *, positions: Optional[Iterable[str]], limit: Optional[int]) -> pd.DataFrame:
        if positions:
            df = df[df["pos"].isin([p.upper() for p in positions])]
        if limit:
            df = df.head(limit)
        return df.reset_index(drop=True)
