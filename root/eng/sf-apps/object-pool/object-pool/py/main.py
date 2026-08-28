class Pool:
    def __init__(self, create, size):
        self._create = create
        self._free = [create() for _ in range(size)]   # заплатили за народження наперед
        self._in_use = set()

    def acquire(self):
        obj = self._free.pop() if self._free else self._create()
        self._in_use.add(obj)
        return obj

    def release(self, obj):
        self._in_use.discard(obj)
        self._free.append(obj)          # назад на полицю, НЕ знищуємо
