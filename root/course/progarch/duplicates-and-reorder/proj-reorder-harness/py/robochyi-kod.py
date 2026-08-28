from __future__ import annotations
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Update:
    device_id: str
    version: int
    value: int


# (1) ДЖЕРЕЛО — монотонний лічильник на кожен пристрій
class Source:
    def __init__(self) -> None:
        self._version: dict[str, int] = {}

    def stamp(self, device_id: str, value: int) -> Update:
        nxt = self._version.get(device_id, 0) + 1          # 1, 2, 3 … окремо на пристрій
        self._version[device_id] = nxt
        return Update(device_id, nxt, value)


# (2) ВАРТОВИЙ — те, що випробовуємо
class Store:
    def __init__(self) -> None:
        self._value: dict[str, int] = {}
        self._applied: dict[str, int] = {}

    def version_of(self, device_id: str) -> int:
        return self._applied.get(device_id, -1)            # −1 = пристрій ще не знайомий

    def apply_update(self, u: Update) -> str:
        if u.version <= self.version_of(u.device_id):
            return "dropped"
        self._value[u.device_id] = u.value
        self._applied[u.device_id] = u.version             # рухаємо межу ЦЬОГО пристрою
        return "applied"

    def snapshot(self) -> dict[str, int]:
        return dict(self._value)


# (3) СТЕНД — одне випробування з фіксованим зерном
def run_trial(seed: int) -> None:
    rnd = random.Random(seed)                              # ГПВЧ на зерні: падіння відтворюване
    source, store = Source(), Store()
    devices = ["living", "bedroom", "hall", "kitchen"]

    # 3a. істинний потік зі зростальними версіями на пристрій
    stream: list[Update] = []
    for d in devices:
        for _ in range(rnd.randint(1, 12)):               # 1..12 оновлень на пристрій
            stream.append(source.stamp(d, rnd.randint(0, 100)))

    # 3b. оракул — найбільша версія на пристрій, незалежно від порядку
    oracle: dict[str, Update] = {}
    for u in stream:
        cur = oracle.get(u.device_id)
        if cur is None or u.version > cur.version:
            oracle[u.device_id] = u

    # 3c. задублювати ×1..3 і перемішати
    scrambled: list[Update] = []
    for u in stream:
        scrambled += [u] * rnd.randint(1, 3)              # 1..3 копії кожного оновлення
    rnd.shuffle(scrambled)

    # 3d. згодувати вартовому у переставленому, задубльованому порядку
    for u in scrambled:
        store.apply_update(u)

    # 3e. ствердити збіг із оракулом + жодних привидів (див. пастку 1)
    final = store.snapshot()
    for d in oracle:
        assert final.get(d) == oracle[d].value, \
            f"seed={seed} {d}: чекали {oracle[d].value} (max версія), маємо {final.get(d)}"
    assert len(final) == len(oracle), f"seed={seed}: привид-пристрій у підсумку"


if __name__ == "__main__":
    for seed in range(1, 10_001):
        run_trial(seed)
    print("10000 випробувань пройдено: копія щоразу зійшлася до правди")
