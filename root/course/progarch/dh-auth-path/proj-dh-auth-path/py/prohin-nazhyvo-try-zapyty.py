ACTIONS_BY_ROLE = {
    "owner":    {"unlock", "lock", "view", "configure"},
    "resident": {"unlock", "lock", "view"},
    "guest":    {"view"},
}
membership = {
    "bohdan": {"home-7": "resident"},     # Богдан — мешканець дому 7
    "guest7": {"home-7": "guest"},        # Гість — лише глядач у домі 7
}
locks = {"42": {"home_id": "home-7"},     # Богданів замок
         "99": {"home_id": "home-3"}}     # Мартин замок

TOKENS = {  # «підпис» = чи є токен у таблиці виданих
    "tok-bohdan": Subject("bohdan", ["device:command", "device:view"]),
    "tok-guest":  Subject("guest7", ["device:view"]),
}
def verify_access_token(auth):
    return TOKENS.get((auth or "").removeprefix("Bearer ")) if auth else None

def can(sub: Subject, action: str, lock: dict) -> bool:
    role = membership.get(sub.id, {}).get(lock["home_id"])   # ключ — дім САМОГО замка
    if role is None:
        return False                                         # не член цього дому → ні (IDOR)
    return action in ACTIONS_BY_ROLE[role]                   # відмова за замовчуванням

# ── Ярус 2: сервіс пристроїв (Брама 2) ──
def devices_service(path: str, att: dict) -> str:
    if att["aud"] != "devices":
        return "Брама2 ✗ 401 (чуже засвідчення)"
    subject = Subject(att["sub"], [])                        # хто — із ЗАСВІДЧЕННЯ
    lock_id = path.split("/")[2]                             # /devices/42/unlock → "42"
    lock = locks.get(lock_id)
    if lock is None:
        return "Брама2 · 404 (нема замка)"
    if not can(subject, "unlock", lock):
        return f"Брама1 ✓ (скоуп є) → засвідчення → Брама2 ✗ 403 (замок #{lock_id} у {lock['home_id']}, не твоєму) — IDOR спіймано"
    return f"Брама1 ✓ → засвідчення → Брама2 ✓ (замок #{lock_id} у домі 7) → 200, замок відчинено"

# ── Ярус 1: шлюз (Брама 1) → засвідчення → сервіс ──
def gateway(path: str, auth: str) -> str:
    subject = verify_access_token(auth)
    if subject is None:
        return "Брама1 ✗ 401 (токен не впізнано)"
    if "device:command" not in subject.scopes:
        return "Брама1 ✗ 403 (нема скоупу device:command) — сервіс не потурбовано"
    attestation = {"sub": subject.id, "aud": "devices"}      # «підписане» шлюзом
    return devices_service(path, attestation)                # переслали ЗАСВІДЧЕННЯ, не токен

for who, path, auth in [
    ("Богдан", "/devices/42/unlock", "Bearer tok-bohdan"),
    ("Гість ", "/devices/42/unlock", "Bearer tok-guest"),
    ("Богдан", "/devices/99/unlock", "Bearer tok-bohdan"),
]:
    print(f"{who} {path:<20} → {gateway(path, auth)}")
