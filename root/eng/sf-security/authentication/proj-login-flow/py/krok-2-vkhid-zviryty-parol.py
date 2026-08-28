from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(memory_cost=19456, time_cost=2, parallelism=1)
# фіктивний хеш із тими самими параметрами — рахуємо один раз під час старту
DUMMY_HASH = ph.hash("dummy-password-never-matches")

def login(email: str, password: str, db):
    norm = email.strip().lower()
    user = db.find_user(norm)                # None, якщо немає
    stored = user.pw_hash if user else DUMMY_HASH
    try:
        ph.verify(stored, password)          # кине VerifyMismatchError, якщо не збіглося
    except VerifyMismatchError:
        return None                          # те саме «ні» на обидва випадки
    return user                              # None → так само вхід не відбувся
