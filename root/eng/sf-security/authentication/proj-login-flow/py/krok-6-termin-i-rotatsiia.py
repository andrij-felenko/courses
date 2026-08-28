IDLE = 60 * 60 * 24 * 7        # 7 діб без активності — просрочка
ABSOLUTE = 60 * 60 * 24 * 14   # 14 діб від входу — жорстка стеля

def authenticate(token: str, db):
    s = db.get_session(_sha256(token))
    if s is None:
        return None
    now = time.time()
    if now - s["last_seen"] > IDLE or now - s["created_at"] > ABSOLUTE:
        db.delete_session(_sha256(token))   # мертву — прибрати
        return None
    db.touch_session(_sha256(token), now)   # ковзне вікно бездіяльності
    return s

# РОТАЦІЯ під час входу — проти фіксації сесії:
def login_and_start(user, old_token, db) -> str:
    if old_token:
        db.delete_session(_sha256(old_token))  # старий ідентифікатор — мертвий
    return create_session(user.id, db)         # свіжий, невідомий нападнику
