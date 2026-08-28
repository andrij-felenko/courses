class CoolingController:
    def __init__(self, clock, store, cooler, policy: Policy) -> None:
        self._clock, self._store, self._cooler, self._policy = clock, store, cooler, policy
    def tick(self) -> None:
        d = decide_cooling(self._store.recent(), self._clock.now(), self._policy)
        (self._cooler.turn_on if d == "on" else self._cooler.turn_off)()

# три тривіальні дублі — кожен рівно за своїм гачком:
class FakeClock:                                            # недетермінований → фейк
    def now(self) -> int: return 1_000_000
class FakeStore:                                            # тримає стан → фейк
    def recent(self) -> list[Reading]:
        return [Reading(1_000_000 - 60_000, 26), Reading(1_000_000 - 10_000, 27)]
class SpyCooler:                                            # незворотний ефект → шпигун
    def __init__(self) -> None: self.calls: list[str] = []
    def turn_on(self) -> None:  self.calls.append("on")
    def turn_off(self) -> None: self.calls.append("off")

def test_controller_turns_on():
    spy = SpyCooler()
    CoolingController(FakeClock(), FakeStore(), spy, Policy(25, 5 * 60_000)).tick()
    assert spy.calls == ["on"]                              # перевірка взаємодії
