"""Workout Logger — Workout service layer."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


class WorkoutService:
    """Workout service for the Workout Logger application."""

    def __init__(
        self,
        store: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._store = store
        self._cfg   = config or {}
        self._calories = self._cfg.get("calories", None)
        logger.debug("%s initialised", self.__class__.__name__)

    def complete_workout(
        self, calories: Any, reps: Any, **extra: Any
    ) -> Dict[str, Any]:
        """Create and persist a new Workout record."""
        now = datetime.now(timezone.utc).isoformat()
        record: Dict[str, Any] = {
            "id":         str(uuid.uuid4()),
            "calories": calories,
            "reps": reps,
            "status":     "active",
            "created_at": now,
            **extra,
        }
        saved = self._store.put(record)
        logger.info("complete_workout: created %s", saved["id"])
        return saved

    def get_workout(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Workout by its *record_id*."""
        record = self._store.get(record_id)
        if record is None:
            logger.debug("get_workout: %s not found", record_id)
        return record

    def log_workout(
        self, record_id: str, **changes: Any
    ) -> Dict[str, Any]:
        """Apply *changes* to an existing Workout."""
        record = self._store.get(record_id)
        if record is None:
            raise KeyError(f"Workout {record_id!r} not found")
        record.update(changes)
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self._store.put(record)

    def skip_workout(self, record_id: str) -> bool:
        """Remove a Workout; returns True on success."""
        if self._store.get(record_id) is None:
            return False
        self._store.delete(record_id)
        logger.info("skip_workout: removed %s", record_id)
        return True

    def list_workouts(
        self,
        status: Optional[str] = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return paginated Workout records."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        results = self._store.find(query, limit=limit, offset=offset)
        logger.debug("list_workouts: %d results", len(results))
        return results

    def iter_workouts(
        self, batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """Yield all Workout records in batches of *batch_size*."""
        offset = 0
        while True:
            page = self.list_workouts(limit=batch_size, offset=offset)
            if not page:
                break
            yield from page
            if len(page) < batch_size:
                break
            offset += batch_size
