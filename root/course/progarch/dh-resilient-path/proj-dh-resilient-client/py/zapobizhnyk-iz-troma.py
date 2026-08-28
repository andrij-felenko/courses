# Запобіжник: closed → open → half. Рішення "пускати?" СИНХРОННЕ (без await),
# тому в однопотоковому asyncio проба гарантовано одна.
from time import monotonic     # МОНОТОННИЙ годинник, не time.time()


class CircuitOpen(Exception):
    retryable = False


class CircuitBreaker:
    def __init__(self, fails_to_open, cooldown):
        self._fails_to_open = fails_to_open
        self._cooldown = cooldown
        self._state = "closed"
        self._fails = 0
        self._opened_at = 0.0
        self._probe = False

    async def call(self, fn):
        if not self._allow():                 # відкритий → НЕ кличемо, миттєво нагору
            raise CircuitOpen()
        try:
            r = await fn()
        except Exception:
            self._on_failure()                # рахуємо ЦЕЙ виклик як відмову
            raise
        self._on_success()
        return r

    def _allow(self):
        if self._state == "closed":
            return True
        if self._state == "open":
            if monotonic() - self._opened_at < self._cooldown:
                return False                  # ще холонемо
            self._state, self._probe = "half", True   # ця спроба — і є проба
            return True
        if self._probe:                       # half: пробу вже взяли
            return False
        self._probe = True
        return True

    def _on_success(self):
        self._state, self._fails, self._probe = "closed", 0, False

    def _on_failure(self):
        if self._state == "half":             # проба впала — знову відкрито
            return self._open()
        self._fails += 1
        if self._fails >= self._fails_to_open:
            self._open()

    def _open(self):
        self._state, self._opened_at, self._fails, self._probe = "open", monotonic(), 0, False
