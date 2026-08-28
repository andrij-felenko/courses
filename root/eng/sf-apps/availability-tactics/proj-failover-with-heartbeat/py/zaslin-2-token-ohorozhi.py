import sys


# Токен кладемо в КОЖЕН запис; сховище відкидає застарілі саме на записі.
class FencedStore:
    def __init__(self):
        self.highest_seen = 0    # найбільший токен, який сховище вже приймало

    # Повертає True, якщо запис прийнято. Це — ЄДИНЕ місце істини про те,
    # хто зараз має право писати. Тут гине розкол мозку.
    def write(self, token: int, data: bytes) -> bool:
        if token < self.highest_seen:
            # запис від відсталого «головного» — мовчки НЕ псуємо дані
            print(f"fenced: токен {token} < {self.highest_seen}, запис відкинуто",
                  file=sys.stderr)
            return False
        self.highest_seen = token    # монотонно піднімаємо планку
        # ... власне запис data ...
        return True
