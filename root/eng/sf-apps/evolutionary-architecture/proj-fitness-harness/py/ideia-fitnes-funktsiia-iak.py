from dataclasses import dataclass
from typing import Callable

# Спільний контракт: усе, що вміє винести вирок про одну вісь системи.
@dataclass(frozen=True)
class Verdict:
    passed: bool
    detail: str                          # куди дивитися, коли не пройшло

@dataclass(frozen=True)
class FitnessFunction:
    name: str
    axis: str                            # яку вісь системи стереже
    run: Callable[[], Verdict]           # виносить вирок
