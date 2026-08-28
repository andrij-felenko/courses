# tests/fitness/test_presence_retention.py
from datetime import datetime, timedelta, timezone
from twin import Twin, RETENTION

def test_presence_not_kept_beyond_window():
    twin = Twin()
    now = datetime(2026, 7, 11, 12, tzinfo=timezone.utc)
    twin.record(now - timedelta(hours=48), True)    # два дні тому
    twin.record(now - timedelta(hours=1),  False)   # година тому
    twin.prune(now)
    # питаємо ЗА ДЕСЯТИЛІТТЯ — і все одно нічого старшого за вікно
    kept = twin.presence_since(now - timedelta(days=3650))
    assert all(ts >= now - RETENTION for ts, _ in kept)
    assert len(kept) == 1
