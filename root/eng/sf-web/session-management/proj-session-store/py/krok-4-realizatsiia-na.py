import secrets, time, json
import redis

IDLE_S = 30 * 60
ABSOLUTE_S = 12 * 3600

_ROTATE = """
local v = redis.call('GET', KEYS[1])
if not v then return nil end
redis.call('SET', KEYS[2], v, 'EX', ARGV[1])
redis.call('DEL', KEYS[1])
return 1
"""

class RedisStore:
    def __init__(self, r: redis.Redis) -> None:
        self._r = r
        self._rotate = r.register_script(_ROTATE)   # Lua — атомарний rotate

    def _key(self, sid: str) -> str:
        return f"sess:{sid}"

    def create(self, user_id: str) -> str:
        sid = secrets.token_urlsafe(18)
        value = json.dumps({"user_id": user_id, "created_at": time.time()})
        self._r.set(self._key(sid), value, ex=IDLE_S, nx=True)
        return sid

    def lookup(self, sid: str) -> dict | None:
        raw = self._r.get(self._key(sid))
        if raw is None:
            return None                              # ключа немає — Redis згасив за idle
        s = json.loads(raw)
        abs_left = s["created_at"] + ABSOLUTE_S - time.time()
        if abs_left <= 0:
            self._r.delete(self._key(sid))           # впала абсолютна стеля
            return None
        self._r.expire(self._key(sid), int(min(IDLE_S, abs_left)))  # ковзання, обмежене абсолютом
        return s

    def rotate(self, sid: str) -> str | None:
        nxt = secrets.token_urlsafe(18)
        ok = self._rotate(keys=[self._key(sid), self._key(nxt)], args=[IDLE_S])
        return nxt if ok else None

    def destroy(self, sid: str) -> None:
        self._r.delete(self._key(sid))
