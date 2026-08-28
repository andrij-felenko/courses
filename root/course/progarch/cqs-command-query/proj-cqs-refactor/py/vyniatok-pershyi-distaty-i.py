from collections import deque

class CommandQueue:
    def __init__(self) -> None:
        self._items: deque = deque()

    def enqueue(self, job) -> None:        # КОМАНДА
        self._items.append(job)

    def dequeue(self):                     # ВИНЯТОК: дістати-й-вилучити
        return self._items.popleft() if self._items else None

    def size(self) -> int:                 # ЗАПИТ
        return len(self._items)
