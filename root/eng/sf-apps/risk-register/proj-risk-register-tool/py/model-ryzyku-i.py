from dataclasses import dataclass
from enum import Enum

class State(Enum):
    OPEN         = "відкритий"        # виявлений, ще не зайнялися
    WATCHED      = "під наглядом"     # тригер зведено, чекаємо
    MITIGATING   = "пом'якшується"    # діємо наперед
    ACCEPTED     = "прийнятий"        # свідомо лишили (залишковий рівень)
    CLOSED       = "закритий"         # минув або пом'якшено — не загрожує
    MATERIALIZED = "матеріалізувався" # став проблемою, пішов з реєстру

# Стани, у яких рядок БІЛЬШЕ НЕ додається до сукупної загрози.
DEAD = {State.CLOSED, State.MATERIALIZED}

@dataclass
class Risk:
    id: str
    desc: str
    p: float        # ймовірність за горизонт, 0.0..1.0
    L: float        # збиток, якщо вдарить (у грошах або днях)
    trigger: str    # спостережна ознака-тригер
    owner: str      # жива людина з іменем, не «команда»
    state: State

# Експозиція рядка — очікуваний збиток p·L, але лише поки рядок АКТИВНИЙ.
def exposure(r: Risk) -> float:
    return 0.0 if r.state in DEAD else r.p * r.L

# Сукупна експозиція портфеля — сума по всіх рядках (лінійність сподівання).
def portfolio(reg: list[Risk]) -> float:
    return sum(exposure(r) for r in reg)
