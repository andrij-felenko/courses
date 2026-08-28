import threading

class Pool:
    def __init__(self, factory, max_size, timeout=5.0):
        self._factory = factory
        self._max = max_size
        self._timeout = timeout
        self._free = []
        self._in_use = set()
        self._created = 0
        self._cond = threading.Condition()       # замок + черга очікування

    def acquire(self):
        with self._cond:                         # ← зайшов один; решта чекає
            deadline = _now() + self._timeout
            while True:
                if self._free:                   # є вільний — беремо
                    conn = self._free.pop()
                    self._in_use.add(conn)
                    return conn
                if self._created < self._max:    # нема — але можна вирости
                    self._created += 1
                    conn = self._factory()
                    self._in_use.add(conn)
                    return conn
                remaining = deadline - _now()    # усе зайнято — чекаємо
                if remaining <= 0:
                    raise PoolExhausted("пул вичерпано")
                self._cond.wait(remaining)       # спить, ВІДПУСКАЮЧИ замок

    def release(self, conn):
        conn.reset()
        with self._cond:
            self._in_use.discard(conn)
            self._free.append(conn)
            self._cond.notify()                  # будить одного, хто чекає
