"""Workout Logger — exception types."""

class WorkoutLoggerError(Exception):
    """Base exception for all Workout Logger errors."""

    def __init__(self, message: str, code: int = 0) -> None:
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {super().__str__()}"


class SessionNotFoundError(WorkoutLoggerError):
    """Raised when a Session record cannot be located."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"Session {record_id!r} not found", code=404)
        self.record_id = record_id


class SessionValidationError(WorkoutLoggerError):
    """Raised when a Session fails field validation."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f"Invalid {field!r}: {reason}", code=422)
        self.field  = field
        self.reason = reason


class WorkoutLoggerConflictError(WorkoutLoggerError):
    """Raised on duplicate or conflicting Workout Logger state."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Conflict: {detail}", code=409)


def raise_if_none(value: object, label: str = "Session") -> object:
    """Raise SessionNotFoundError if *value* is None."""
    if value is None:
        raise SessionNotFoundError(label)
    return value
