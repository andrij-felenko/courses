from collections import deque
from dataclasses import dataclass, field


# --- Контейнер 1: буфер-черга (коробка "Черга" на діаграмі) ---
@dataclass
class SampleQueue:
    data: deque[int] = field(default_factory=lambda: deque(maxlen=64))

    def push(self, v: int) -> bool:
        if len(self.data) == self.data.maxlen:
            return False
        self.data.append(v)
        return True

    def pop(self) -> int | None:
        return self.data.popleft() if self.data else None


# --- Контейнер 2: сенсорний вузол ---
# Стрілка діаграми "сенсор -> черга" стає ПОЛЕМ-залежністю:
# сенсор знає про чергу рівно тому, що на діаграмі є ця стрілка.
@dataclass
class SensorNode:
    out: SampleQueue   # єдиний дозволений зв'язок — до черги

    def tick(self, reading: int) -> None:
        self.out.push(reading)   # сенсор торкає ЛИШЕ чергу, як на діаграмі


# --- Контейнер 3: передавач у мережу ---
@dataclass
class Uplink:
    in_: SampleQueue   # стрілка "передавач -> черга", теж поле

    def tick(self) -> None:
        while (v := self.in_.pop()) is not None:
            pass  # відправити v у мережу
