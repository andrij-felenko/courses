import threading

class ViewCounter:
    def __init__(self) -> None:
        self._hits = 0
        self._lock = threading.Lock()

    # Чесний виняток: І міняє, І повертає — але НЕПОДІЛЬНО.
    def next_view_number(self) -> int:
        with self._lock:        # секцію не розірве інший потік
            self._hits += 1     # зміна
            return self._hits   # і повернення разом — атомарно
