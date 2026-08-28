class Pool:
    def __init__(self, factory, size):
        self._factory = factory                 # як народити Conn: () -> Conn
        self._free = [factory() for _ in range(size)]   # заплатили наперед
        self._in_use = set()

    def acquire(self):
        conn = self._free.pop()                  # знімаємо з полиці
        self._in_use.add(conn)                   # → in-use
        return conn

    def release(self, conn):
        conn.reset()                             # ← стерти чужий стан ДО полиці
        self._in_use.discard(conn)               # більше не in-use
        self._free.append(conn)                  # → free, чистим

pool = Pool(factory=Conn.open, size=8)           # 8 дорогих з'єднань — раз
conn = pool.acquire()
conn.query("select 1")
pool.release(conn)                               # повернули чистим
