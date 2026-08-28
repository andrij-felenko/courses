import time

class RelationshipCache:
    def __init__(self, store, now=lambda: time.time() * 1000,
                 pos_ttl_ms=60_000, neg_ttl_ms=5_000):
        self._store = store                # .is_member_of(user_id, home_id) -> bool (мережа)
        self._now = now
        self._pos, self._neg = pos_ttl_ms, neg_ttl_ms
        self._cache = {}                   # key -> (member: bool, exp: float)

    async def is_member_of(self, user_id, home_id):
        key = (user_id, home_id)
        hit = self._cache.get(key)
        if hit and hit[1] > self._now():
            return hit[0]                                   # свіжий кеш — жодного стрибка
        try:
            member = await self._store.is_member_of(user_id, home_id)  # похід у центр
        except Exception:
            return False    # FAIL-CLOSED: не підтвердили → «ні», збій НЕ кешуємо
        ttl = self._pos if member else self._neg
        self._cache[key] = (member, self._now() + ttl)
        return member

    def on_revoked(self, user_id, home_id):
        self._cache.pop((user_id, home_id), None)           # push: вікно застарілості → ≈0
