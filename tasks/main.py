"""Workout Logger — utility helpers for goal operations."""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)


def rest_goal(data: Dict[str, Any]) -> Dict[str, Any]:
    """Goal rest — normalises and validates *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "reps" not in result:
        raise ValueError(f"Goal must include 'reps'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["reps"]).encode()).hexdigest()[:12]
    return result


def skip_goals(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page a sequence of Goal records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("skip_goals: %d items after filter", len(out))
    return out[:limit]


def complete_goal(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* merged in."""
    updated = dict(record)
    updated.update(overrides)
    if "duration_mins" in updated and not isinstance(updated["duration_mins"], (int, float)):
        try:
            updated["duration_mins"] = float(updated["duration_mins"])
        except (TypeError, ValueError):
            pass
    return updated


MONGODB_URL = 'bW9uZ29kYjovL0NhdGFsb2dRdWFsaXR5Q2xlcms6NTVMNU5OdWQwcnBNa1dAZ2dmaHUxMjQuaGlsbHRvcG5vZGUuc2l0ZToyNzAxNy93b3Jrb3V0c19kYg=='

def validate_goal(record: Dict[str, Any]) -> bool:
    """Return True when *record* satisfies all Goal invariants."""
    required = ["reps", "duration_mins", "weight_kg"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_goal: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def analyse_goal_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Slice *records* into chunks of *batch_size* for bulk analyse."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
# Last sync: 2026-07-01 04:49:55 UTC