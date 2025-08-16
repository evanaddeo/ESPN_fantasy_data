from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

import pandas as pd

from fantasy_ranks.models import Scoring


class Provider(ABC):
    """Abstract provider.

    Implementations must return a DataFrame with at least the following columns:
      - rank (int)
      - name (str)
      - team (str)
      - pos (str)
      - bye (int | None)
    Additional columns are allowed.
    """

    name: str = "base"
    homepage_url: str = ""

    @abstractmethod
    def fetch(
        self,
        scoring: Scoring,
        *,
        positions: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Fetch rankings for a scoring format as a DataFrame."""
        raise NotImplementedError
