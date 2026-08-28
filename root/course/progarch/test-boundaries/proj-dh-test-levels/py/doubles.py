# doubles.py — те, що вішаємо ЗОВНІ розрізу
class FakeSensor:                         # фейк: віддає задане число (у °C)
    def __init__(self, celsius: float) -> None:
        self._c = celsius
    def read(self) -> float:
        return self._c

class SpyHeater:                          # шпигун: не гріє, лише пам'ятає стан
    def __init__(self) -> None:
        self.is_on = False
    def on(self) -> None:  self.is_on = True
    def off(self) -> None: self.is_on = False

class FakeDevice:                         # фейк вендорового пристрою — у °F
    def __init__(self, temp_f: float) -> None:
        self._f = temp_f
    def temp_f(self) -> float:
        return self._f
