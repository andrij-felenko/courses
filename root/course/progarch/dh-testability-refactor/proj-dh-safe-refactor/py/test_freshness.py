# test_freshness.py — характеризація: пришпилюємо ВАДУ, зелену вже сьогодні
from hub import Reading, Config, tick          # той самий дім за швами

class FakeSensor:                               # фейк: віддає задані виміри, один за одним
    def __init__(self, *readings): self._q = list(readings)
    def read(self) -> Reading: return self._q.pop(0)

class SpyHeater:                                # шпигун: нічого не гріє, лише пам'ятає виклики
    def __init__(self): self.calls = []
    def on(self):  self.calls.append("on")
    def off(self): self.calls.append("off")

def test_stuck_sensor_heats_forever_TODAY():    # що Є, не що має бути
    heater = SpyHeater()
    stuck = FakeSensor(*[Reading(19.9)] * 5)    # давач завис на 19.9 °C — під порогом
    for _ in range(5):
        tick(stuck, heater, Config(threshold=20.0))
    assert heater.calls == ["on"] * 5           # v1 гріє безкінечно — задокументовано
