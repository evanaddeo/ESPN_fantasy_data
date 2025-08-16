from __future__ import annotations

import os
import re
import time
from datetime import date
from typing import Iterable, List, Optional

import httpx
import pandas as pd
from bs4 import BeautifulSoup

from fantasy_ranks.models import PlayerRank, Scoring
from fantasy_ranks.providers.base import Provider
from fantasy_ranks.utils.caching import cache_get, cache_put


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)


class YahooEditorialProvider(Provider):
    name = "yahoo-editorial"
    homepage_url = "https://sports.yahoo.com/fantasy/football/"

    def fetch(
        self,
        scoring: Scoring,
        *,
        positions: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
        season: Optional[int] = None,
        include_def_k: bool = True,
    ) -> pd.DataFrame:
        season = season or date.today().year
        url = self._resolve_url(scoring=scoring, season=season)

        cache_key = f"v1::yahoo-editorial::{season}::{scoring}::{url}"
        cached = cache_get(cache_key)
        if cached is not None:
            df = pd.DataFrame(cached)
            if not df.empty and {"rank", "name", "team", "pos"}.issubset(df.columns):
                return self._finalize_df(df, positions=positions, limit=limit, include_def_k=include_def_k)

        if not (url.startswith("http://") or url.startswith("https://")):
            df = self._sample()
        else:
            html = self._fetch_html(url)
            df = self._parse_html_to_df(html, scoring=scoring, include_def_k=include_def_k)
        if df.empty:
            df = self._sample()

        cache_put(cache_key, df.to_dict(orient="records"))
        return self._finalize_df(df, positions=positions, limit=limit, include_def_k=include_def_k)

    def _resolve_url(self, *, scoring: Scoring, season: int) -> str:
        override = os.getenv("FANTASY_RANKS_YAHOO_URL")
        if override:
            return override
        return self.homepage_url

    def _fetch_html(self, url: str) -> str:
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
        last_exc: Optional[Exception] = None
        for attempt in range(4):
            try:
                with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
                    resp = client.get(url)
                    resp.raise_for_status()
                    return resp.text
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                time.sleep(0.8 * (attempt + 1))
        raise RuntimeError(f"Failed to fetch Yahoo editorial page: {url}\n{last_exc}")

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", text.replace("\xa0", " ").strip())

    def _parse_table(self, table: BeautifulSoup) -> List[dict]:
        headers = [self._clean(th.get_text(" ")) for th in table.select("thead th, tr th")]
        rows: List[dict] = []
        for tr in table.select("tbody tr, tr"):
            cells = [self._clean(td.get_text(" ")) for td in tr.find_all(["td", "th"])]
            if not cells or all(c == "" for c in cells):
                continue
            if not cells[0].isdigit():
                continue
            row = self._row_from_cells(headers, cells)
            if row:
                rows.append(row)
        return rows

    def _row_from_cells(self, headers: List[str], cells: List[str]) -> Optional[dict]:
        colmap = {h.upper(): i for i, h in enumerate(headers)}
        try:
            rank_str = cells[colmap.get("RK", 0)]
            player = cells[colmap.get("PLAYER", 1)]
            team = cells[colmap.get("TEAM", 2)]
            pos = cells[colmap.get("POS", 3)]
            bye_str = cells[colmap.get("BYE", 4)] if "BYE" in colmap else ""
        except Exception:
            return None
        if not rank_str.isdigit():
            return None
        bye = int(bye_str) if bye_str.isdigit() else None
        pos = pos.upper().strip()
        if pos in {"D/ST", "DST"}:
            pos = "DST"
        else:
            pos = pos.split("/")[0]
        return {
            "rank": int(rank_str),
            "name": self._clean(player),
            "team": self._clean(team).upper(),
            "pos": pos,
            "bye": bye,
            "source": self.name,
            "scoring": "ppr",
            "date": date.today().isoformat(),
        }

    def _parse_html_to_df(self, html: str, *, scoring: Scoring, include_def_k: bool) -> pd.DataFrame:
        soup = BeautifulSoup(html, "lxml")
        rows: List[dict] = []
        for table in soup.find_all("table"):
            rows.extend(self._parse_table(table))
        df = pd.DataFrame(rows)
        if not include_def_k and not df.empty:
            df = df[~df["pos"].isin(["K", "DST"])].copy()
        # Validate subset via Pydantic
        valid = []
        for rec in df.to_dict(orient="records"):
            try:
                item = PlayerRank(
                    name=rec["name"],
                    team=rec["team"],
                    pos=rec["pos"],
                    rank=int(rec["rank"]),
                    bye=rec.get("bye"),
                    source=self.name,
                    scoring=scoring,
                    date=date.today(),
                )
                valid.append(item.model_dump())
            except Exception:
                continue
        return pd.DataFrame(valid)

    def _sample(self) -> pd.DataFrame:
        sample = [
            {"rank": 1, "name": "Yahoo Sample RB", "team": "AAA", "pos": "RB", "bye": None},
            {"rank": 2, "name": "Yahoo Sample WR", "team": "BBB", "pos": "WR", "bye": None},
        ]
        df = pd.DataFrame(sample)
        df["source"] = self.name
        df["scoring"] = "ppr"
        df["date"] = date.today().isoformat()
        return df

    def _finalize_df(
        self,
        df: pd.DataFrame,
        *,
        positions: Optional[Iterable[str]],
        limit: Optional[int],
        include_def_k: bool,
    ) -> pd.DataFrame:
        if positions:
            df = df[df["pos"].isin([p.upper() for p in positions])]
        if limit:
            df = df.head(limit)
        if not include_def_k:
            df = df[~df["pos"].isin(["K", "DST"])].copy()
        return df.reset_index(drop=True)


