from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable


def _is_utc_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() == timedelta(0)


@dataclass(frozen=True)
class TemporaryBarrier:
    edge_id: str
    created_at: datetime
    expires_at: datetime
    reason: str

    def __post_init__(self) -> None:
        if not self.edge_id or not self.reason.strip():
            raise ValueError("Barrier edge and reason must be non-empty")
        if not _is_utc_aware(self.created_at) or not _is_utc_aware(self.expires_at):
            raise ValueError("Barrier timestamps must be UTC-aware")
        if self.expires_at <= self.created_at:
            raise ValueError("Barrier expires_at must be after created_at")

    def is_active(self, now: datetime) -> bool:
        if not _is_utc_aware(now):
            raise ValueError("Current time must be UTC-aware")
        return self.created_at <= now < self.expires_at


def active_barrier_ids(
    barriers: Iterable[TemporaryBarrier],
    now: datetime,
) -> frozenset[str]:
    return frozenset(barrier.edge_id for barrier in barriers if barrier.is_active(now))
