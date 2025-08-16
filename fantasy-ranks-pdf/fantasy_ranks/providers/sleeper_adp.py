from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from fantasy_ranks.models import Scoring
from fantasy_ranks.providers.base import Provider


class SleeperADPProvider(Provider):
    name = "sleeper-adp"
    homepage_url = "https://sleeper.com/"

    def fetch(
        self,
        scoring: Scoring,
        *,
        positions: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Optional Sleeper ADP provider.

        TODO: Fetch ADP data via Sleeper public endpoints and normalize.
        """
        raise NotImplementedError("Sleeper ADP provider is not implemented yet")
