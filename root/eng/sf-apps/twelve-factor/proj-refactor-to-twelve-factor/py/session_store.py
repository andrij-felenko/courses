# session_store.py — сесії ЗАЛОГІНЕНИХ живуть у спільному Redis, не в процесі.
import redis
from config import config

# Клієнт до спільного кешу; адреса — теж із середовища (крок 1).
r = redis.from_url(config.REDIS_URL)

SESSION_TTL = 3600   # сесія живе годину без активності

def remember_login(sid: str, user_id: int) -> None:
    # Було: logged_in_users[sid] = user_id  (у пам'яті ЦЬОГО процесу)
    r.setex(f"session:{sid}", SESSION_TTL, user_id)   # ← у СПІЛЬНОМУ кеші

def whoami(sid: str) -> int | None:
    value = r.get(f"session:{sid}")
    return int(value) if value else None   # None → сесія протухла або чужа
