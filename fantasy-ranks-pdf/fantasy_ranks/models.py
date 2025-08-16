from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field

Scoring = Literal["ppr", "half", "standard"]


class ScoringEnum(str, Enum):
    ppr = "ppr"
    half = "half"
    standard = "standard"


class PlayerRank(BaseModel):
    """Represents a single player's ranking row.

    Attributes:
        name: Player full name.
        team: Team abbreviation, e.g., "KC".
        pos: Position, e.g., "RB".
        rank: Overall rank (1..N).
        bye: Optional bye week number.
        source: Data source identifier, e.g., "espn-editorial".
        scoring: Scoring format used.
        date: Ranking publication or fetch date.
        notes: Optional free-form notes.
    """

    name: str
    team: str
    pos: Literal["QB", "RB", "WR", "TE", "K", "DST"]
    rank: int
    bye: Optional[int] = None
    source: str = Field(default="espn-editorial")
    scoring: Scoring
    date: date
    notes: Optional[str] = None
