from collections import deque

class InMemoryQueue:
    def __init__(self):
        self._items = deque()
    def enqueue(self, type_, payload):
        self._items.append({"type": type_, "payload": payload})
    def take(self):
        return self._items.popleft() if self._items else None
    def depth(self):
        return len(self._items)
