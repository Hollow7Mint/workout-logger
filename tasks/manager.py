"""Workout Logger — Set repository."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class WorkoutManager:
    """Thin repository wrapper for Set persistence in Workout Logger."""

    TABLE = "sets"

    def __init__(self, db: Any) -> None:
        self._db = db
        logger.debug("WorkoutManager bound to %s", db)

    def insert(self, completed_at: Any, reps: Any, **kwargs: Any) -> str:
        """Persist a new Set row and return its generated ID."""
        rec_id = str(uuid.uuid4())
        row: Dict[str, Any] = {
            "id":         rec_id,
            "completed_at": completed_at,
            "reps": reps,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        self._db.insert(self.TABLE, row)
        return rec_id

    def fetch(self, rec_id: str) -> Optional[Dict[str, Any]]:
        """Return the Set row for *rec_id*, or None."""
        return self._db.fetch(self.TABLE, rec_id)

    def update(self, rec_id: str, **fields: Any) -> bool:
        """Patch *fields* on an existing Set row."""
        if not self._db.exists(self.TABLE, rec_id):
            return False
        fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._db.update(self.TABLE, rec_id, fields)
        return True

    def delete(self, rec_id: str) -> bool:
        """Hard-delete a Set row; returns False if not found."""
        if not self._db.exists(self.TABLE, rec_id):
            return False
        self._db.delete(self.TABLE, rec_id)
        return True

    def query(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit:    int = 100,
        offset:   int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return (rows, total_count) for the given *filters*."""
        rows  = self._db.select(self.TABLE, filters or {}, limit, offset)
        total = self._db.count(self.TABLE, filters or {})
        logger.debug("query sets: %d/%d", len(rows), total)
        return rows, total

    def log_by_weight_kg(
        self, value: Any, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch sets filtered by *weight_kg*."""
        rows, _ = self.query({"weight_kg": value}, limit=limit)
        return rows

    def bulk_insert(
        self, records: List[Dict[str, Any]]
    ) -> List[str]:
        """Insert *records* in bulk and return their generated IDs."""
        ids: List[str] = []
        for rec in records:
            rec_id = self.insert(
                rec["completed_at"], rec.get("reps"),
                **{k: v for k, v in rec.items() if k not in ("completed_at", "reps")}
            )
            ids.append(rec_id)
        logger.info("bulk_insert sets: %d rows", len(ids))
        return ids
