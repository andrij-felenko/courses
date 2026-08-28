# doubles.py
from home import Reading, Sensor, Heater

class FakeSensor:                       # фейк: віддає задані виміри, один за одним
    def __init__(self, *readings: Reading):
        self._q = list(readings)
    def read(self) -> Reading:
        return self._q.pop(0)           # порожня черга → IndexError, і це добре (див. пастки)

class SpyHeater:                        # шпигун: нічого не гріє, лише пам'ятає виклики
    def __init__(self):
        self.calls: list[str] = []
    def on(self):  self.calls.append("on")
    def off(self): self.calls.append("off")
