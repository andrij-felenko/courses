import queue

class Pool:
    def __init__(self, factory, max_size, timeout=5.0):
        self._factory = factory
        self._max = max_size
        self._timeout = timeout
        self._free = queue.LifoQueue()           # полиця з вбудованим замком
        self._created = 0                        # скільки взагалі народили
        self._lock = __import__("threading").Lock()   # захищає лічильник

    def acquire(self):
        # 1. Є вільний прямо зараз? Забираємо без чекання.
        try:
            return self._free.get_nowait()
        except queue.Empty:
            pass
        # 2. Ще не доросли до межі? Народжуємо новий (політика A).
        with self._lock:
            if self._created < self._max:
                self._created += 1
                return self._factory()           # дорога плата — раз на об'єкт
        # 3. Межу досягнуто — чекаємо звільнення до таймаута (B + C).
        try:
            return self._free.get(timeout=self._timeout)
        except queue.Empty:
            raise PoolExhausted(
                "усі %d об'єктів зайняті понад %.1f с" % (self._max, self._timeout))

    def release(self, conn):
        conn.reset()
        self._free.put(conn)                     # розбудить того, хто чекає в (3)

class PoolExhausted(Exception):
    pass
