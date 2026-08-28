import secrets, time, threading

IDLE_S = 30 * 60          # ковзний простій: 30 хв
ABSOLUTE_S = 12 * 3600    # тверда стеля: 12 год

class MemoryStore:
    def __init__(self) -> None:
        self._map: dict[str, dict] = {}
        self._lock = threading.Lock()      # кілька потоків можуть лізти водночас

    def create(self, user_id: str) -> str:
        sid = secrets.token_urlsafe(18)
        now = time.time()
        with self._lock:
            self._map[sid] = {"user_id": user_id, "created_at": now, "last_seen": now}
        return sid

    def lookup(self, sid: str) -> dict | None:
        now = time.time()
        with self._lock:
            r = self._map.get(sid)
            if r is None:
                return None
            if now - r["last_seen"] > IDLE_S or now - r["created_at"] > ABSOLUTE_S:
                del self._map[sid]         # згасла за простоєм АБО впала абсолютна стеля
                return None
            r["last_seen"] = now           # ковзання
            return {"user_id": r["user_id"], "created_at": r["created_at"]}

    def rotate(self, sid: str) -> str | None:
        with self._lock:
            r = self._map.pop(sid, None)   # старий номер мертвий тієї ж миті
            if r is None:
                return None
            nxt = secrets.token_urlsafe(18)
            r["last_seen"] = time.time()
            self._map[nxt] = r
            return nxt

    def destroy(self, sid: str) -> None:
        with self._lock:
            self._map.pop(sid, None)

    def sweep(self) -> None:               # кликати періодично (напр., раз на хвилину)
        now = time.time()
        with self._lock:
            dead = [s for s, r in self._map.items()
                    if now - r["last_seen"] > IDLE_S or now - r["created_at"] > ABSOLUTE_S]
            for s in dead:
                del self._map[s]
