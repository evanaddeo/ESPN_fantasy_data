from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from fantasy_ranks.models import Scoring
from fantasy_ranks.providers.base import Provider


class ESPNAPIProvider(Provider):
    name = "espn-api"
    homepage_url = "https://fantasy.espn.com/"

    def __init__(self, *, espn_s2: Optional[str] = None, swid: Optional[str] = None) -> None:
        self.espn_s2 = espn_s2
        self.swid = swid

    def fetch(
        self,
        scoring: Scoring,
        *,
        positions: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Optional projections-based provider.

        TODO: Implement ESPN private API calls when cookies are provided.
        """
        raise NotImplementedError("ESPN API provider is not implemented yet")
