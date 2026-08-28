# test_thermostat.py — женемо крізь шов підробки. decide НЕ редагуємо.
from thermostat import decide


class FakeSensor:
    """Давач-підробка: завжди віддає заготовлений показник."""
    def __init__(self, reads: float) -> None:
        self._reads = reads
    def read(self) -> float:
        return self._reads


class SpyHeater:
    """Розетка-шпигун: нічого не гріє, лише записує, що їй наказали."""
    def __init__(self) -> None:
        self.calls: list[str] = []
    def on(self) -> None:
        self.calls.append("on")
    def off(self) -> None:
        self.calls.append("off")


def test_cold_turns_on():
    spy = SpyHeater()
    decide(FakeSensor(reads=19.0), spy, threshold=20.0)   # 19.0 < 20.0 → холодно
    assert spy.calls == ["on"]


def test_warm_turns_off():
    spy = SpyHeater()
    decide(FakeSensor(reads=21.0), spy, threshold=20.0)   # 21.0 ≥ 20.0 → тепло
    assert spy.calls == ["off"]


def test_boundary_is_off():
    spy = SpyHeater()
    decide(FakeSensor(reads=20.0), spy, threshold=20.0)   # рівно поріг: 20.0 < 20.0 хибно
    assert spy.calls == ["off"]                            # «<» строгий — на порозі НЕ гріємо
