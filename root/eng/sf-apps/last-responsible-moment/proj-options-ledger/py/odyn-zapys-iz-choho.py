from dataclasses import dataclass
from enum import Enum

class Status(str, Enum):
    OPEN = "open"; ARMED = "armed"; DUE = "due"; SUPERSEDED = "superseded"

@dataclass
class Condition:
    signal: str        # ключ метрики, напр. "search.p99_ms"
    direction: str     # "rising" | "falling" — куди «погано»
    arm_at: float      # поріг зведення — увійти в смугу спостереження
    fire_at: float     # поріг спрацювання (для rising: arm_at ≤ fire_at)

@dataclass
class Trigger:
    conditions: list[Condition]
    mode: str = "all"          # "all" | "any"
    hold_for: int = 3          # скільки вимірів поспіль умова має триматися
    lead_weeks: float = 0.0    # L — горизонт прогнозу = час на втілення

@dataclass
class Decision:
    id: str
    title: str
    options: list[str]         # живі альтернативи, ще на столі
    uncertainty: str           # який факт чекаємо дізнатися
    trigger: Trigger
    owner: str                 # хто відповідає, коли настане момент
    adr: str                   # ADR, що фіксує саме відкладання
    status: Status = Status.OPEN
    hold_count: int = 0        # скільки вимірів поспіль трималося спрацювання
