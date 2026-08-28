# conftest.py — дублери для ВСІХ характеризаційних тестів планувальника
import random
from datetime import datetime
import scheduler


class FrozenClock:
    """Дублер годинника: .now() завжди віддає ту саму мить."""
    def __init__(self, moment):
        self._moment = moment
    def now(self):
        return self._moment


def freeze(monkeypatch, hour, seed=0):
    # ВАЖЛИВО: FrozenClock будуємо зі СПРАВЖНЬОГО datetime, а не з уже підміненого —
    # інакше на другому виклику підсунемо самі собі зіпсоване ім'я (див. пастки).
    monkeypatch.setattr(scheduler, "datetime", FrozenClock(datetime(2026, 1, 15, hour, 0)))
    monkeypatch.setattr(scheduler, "random", random.Random(seed))   # зерно 0 → відтворно
