import hashlib, secrets, time

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def create_session(user_id: str, db) -> str:
    token = secrets.token_urlsafe(16)
    now = time.time()
    # зберігаємо лише відбиток, не сам жетон
    db.put_session(_sha256(token),
                   {"user_id": user_id, "created_at": now, "last_seen": now})
    return token

def resolve_session(token: str, db):
    return db.get_session(_sha256(token))    # пошук за відбитком
