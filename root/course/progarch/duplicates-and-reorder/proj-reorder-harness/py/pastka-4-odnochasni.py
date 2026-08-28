# Python: GIL НЕ рятує — між dict.get і dict.set багато байткодів, і перемикання
# потоків може влучити всередину. Потрібен явний замок НА КОЖЕН пристрій:
import threading


class SafeStore(Store):
    def __init__(self) -> None:
        super().__init__()
        self._locks: dict[str, threading.Lock] = {}
        self._guard = threading.Lock()

    def apply_update(self, u: Update) -> str:
        with self._guard:                                  # захистити саму мапу замків
            lock = self._locks.setdefault(u.device_id, threading.Lock())
        with lock:                                         # неподільно НА ЦЕЙ пристрій
            return super().apply_update(u)
