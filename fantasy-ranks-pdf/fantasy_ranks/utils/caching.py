from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from platformdirs import user_cache_dir

APP_NAME = "fantasy-ranks-pdf"
CACHE_TTL_ENV = "FANTASY_RANKS_CACHE_TTL_SECONDS"
DEFAULT_TTL_SECONDS = 3600


@dataclass
class CacheEntry:
    created_at: datetime
    data: Any


def _cache_dir() -> Path:
    return Path(user_cache_dir(APP_NAME, APP_NAME))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _key_to_path(key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return _cache_dir() / f"{digest}.json"


def get_ttl_seconds() -> int:
    raw = os.getenv(CACHE_TTL_ENV)
    if not raw:
        return DEFAULT_TTL_SECONDS
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_TTL_SECONDS
    return max(0, value)


def cache_put(key: str, data: Any) -> None:
    path = _key_to_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"created_at": _now().isoformat(), "data": data}
    path.write_text(json.dumps(payload))


def cache_get(key: str, *, ttl_seconds: Optional[int] = None) -> Optional[Any]:
    path = _key_to_path(key)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text())
        created_at = datetime.fromisoformat(payload["created_at"])  # type: ignore[arg-type]
        ttl = get_ttl_seconds() if ttl_seconds is None else ttl_seconds
        if _now() - created_at > timedelta(seconds=ttl):
            return None
        return payload["data"]
    except Exception:
        return None
