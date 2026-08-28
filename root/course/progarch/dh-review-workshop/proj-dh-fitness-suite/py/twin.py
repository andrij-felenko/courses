# twin.py — присутність не переживає домовленого вікна
from datetime import datetime, timedelta, timezone

RETENTION = timedelta(hours=24)          # міра з ADR: скільки тримаємо присутність

class Twin:
    def __init__(self):
        self._events = []                # (ts, present)
    def record(self, ts, present):
        self._events.append((ts, present))
    def prune(self, now):
        cutoff = now - RETENTION
        self._events = [e for e in self._events if e[0] >= cutoff]
    def presence_since(self, cutoff):    # публічний шлях читання
        return [e for e in self._events if e[0] >= cutoff]
