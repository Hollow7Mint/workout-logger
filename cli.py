"""Workout Logger — utility helpers for session operations."""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)


def skip_session(data: Dict[str, Any]) -> Dict[str, Any]:
    """Session skip — normalises and validates *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "duration_mins" not in result:
        raise ValueError(f"Session must include 'duration_mins'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["duration_mins"]).encode()).hexdigest()[:12]
    return result


def complete_sessions(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page a sequence of Session records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("complete_sessions: %d items after filter", len(out))
    return out[:limit]


def plan_session(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* merged in."""
    updated = dict(record)
    updated.update(overrides)
    if "weight_kg" in updated and not isinstance(updated["weight_kg"], (int, float)):
        try:
            updated["weight_kg"] = float(updated["weight_kg"])
        except (TypeError, ValueError):
            pass
    return updated


def validate_session(record: Dict[str, Any]) -> bool:
    """Return True when *record* satisfies all Session invariants."""
    required = ["duration_mins", "weight_kg", "calories"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_session: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def analyse_session_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Slice *records* into chunks of *batch_size* for bulk analyse."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
