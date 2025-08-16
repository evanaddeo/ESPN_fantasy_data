from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

import pandas as pd

from fantasy_ranks.models import Scoring
from fantasy_ranks.providers.base import Provider


class ESPNEditorialProvider(Provider):
    name = "espn-editorial"
    homepage_url = "https://www.espn.com/fantasy/football/"

    def fetch(
        self,
        scoring: Scoring,
        *,
        positions: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Stub fetch.

        TODO: Implement resilient scraping that detects editorial tables or downloadable sheets.
        Use httpx + beautifulsoup4 + lxml. Normalize to the standard columns.
        """
        data = [
            {"rank": 1, "name": "Justin Jefferson", "team": "MIN", "pos": "WR", "bye": 6},
            {"rank": 2, "name": "Christian McCaffrey", "team": "SF", "pos": "RB", "bye": 9},
            {"rank": 3, "name": "Ja'Marr Chase", "team": "CIN", "pos": "WR", "bye": 12},
            {"rank": 4, "name": "CeeDee Lamb", "team": "DAL", "pos": "WR", "bye": 7},
        ]
        df = pd.DataFrame(data, columns=["rank", "name", "team", "pos", "bye"]).sort_values("rank")
        if positions:
            df = df[df["pos"].isin(list(positions))]
        if limit:
            df = df.head(limit)
        # Add metadata columns optionally used downstream
        df["source"] = self.name
        df["scoring"] = scoring
        df["date"] = date.today().isoformat()
        return df.reset_index(drop=True)
