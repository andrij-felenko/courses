import threading

class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counts: dict[str, int] = {}

    def bump(self, name: str) -> None:
        with self._lock:                                    # рівно ОДНЕ місце мутації
            self._counts[name] = self._counts.get(name, 0) + 1

    def value(self, name: str) -> int:
        with self._lock:
            return self._counts.get(name, 0)
