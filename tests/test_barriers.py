from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from accesstrace.barriers import TemporaryBarrier, active_barrier_ids


NOW = datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc)


class TemporaryBarrierTests(unittest.TestCase):
    def test_barrier_is_active_before_expiry(self) -> None:
        barrier = TemporaryBarrier(
            edge_id="1:2",
            created_at=NOW,
            expires_at=NOW + timedelta(hours=1),
            reason="construction",
        )

        self.assertTrue(barrier.is_active(NOW + timedelta(minutes=30)))

    def test_barrier_is_inactive_at_expiry(self) -> None:
        barrier = TemporaryBarrier(
            edge_id="1:2",
            created_at=NOW,
            expires_at=NOW + timedelta(hours=1),
            reason="construction",
        )

        self.assertFalse(barrier.is_active(NOW + timedelta(hours=1)))

    def test_returns_only_active_barrier_ids(self) -> None:
        barriers = (
            TemporaryBarrier("1:2", NOW, NOW + timedelta(hours=1), "construction"),
            TemporaryBarrier("2:3", NOW - timedelta(hours=2), NOW - timedelta(hours=1), "expired"),
        )

        self.assertEqual(active_barrier_ids(barriers, NOW), frozenset({"1:2"}))

    def test_rejects_non_utc_or_invalid_time_window(self) -> None:
        with self.assertRaisesRegex(ValueError, "UTC-aware"):
            TemporaryBarrier("1:2", NOW.replace(tzinfo=None), NOW, "construction")
        with self.assertRaisesRegex(ValueError, "after created_at"):
            TemporaryBarrier("1:2", NOW, NOW, "construction")


if __name__ == "__main__":
    unittest.main()
