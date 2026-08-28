# Оренда: право на роль, дійсне до expiry_ms; треба продовжувати.
class Lease:
    def __init__(self, token: int, expiry_ms: int):
        self.token = token          # монотонний токен цього періоду оренди
        self.expiry_ms = expiry_ms  # до якого моменту оренда дійсна


# lease_renew(lease, now_ms) -> bool  — продовжити в арбітра
# demote_self()                       — розжалувати себе в резерв

# Головний зобов'язаний звати це часто. Якщо оренда згасла — НЕГАЙНО
# припинити виконувати роль, ще ДО спроби писати.
def primary_guard(f: Failover, lease: Lease, now_ms: int) -> None:
    if not lease_renew(lease, now_ms) or now_ms >= lease.expiry_ms:
        # ми більше не маємо права бути головним — можливо, нас уже
        # замінили, поки ми висіли. Складаємо роль самі.
        stop_serving()
        demote_self()
        f.role = Role.STANDBY
