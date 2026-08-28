from dataclasses import dataclass
from enum import Enum, auto

# Якісний атрибут, про який дбає стейкхолдер.
class Attribute(Enum):
    AVAILABILITY  = auto()
    MODIFIABILITY = auto()
    PERFORMANCE   = auto()
    SECURITY      = auto()
    COST          = auto()

ATTR_NAME = {
    Attribute.AVAILABILITY:  "доступність",
    Attribute.MODIFIABILITY: "змінюваність",
    Attribute.PERFORMANCE:   "швидкодія",
    Attribute.SECURITY:      "безпека",
    Attribute.COST:          "вартість",
}

@dataclass
class Stakeholder:
    name: str
    power: int           # 1..5 — наскільки може впливати на рішення
    concern: Attribute   # головна турбота цієї людини

reg = [
    Stakeholder("Замовник",   5, Attribute.COST),
    Stakeholder("Оператор",   2, Attribute.AVAILABILITY),   # тихий, але з великою ставкою
    Stakeholder("Супровід",   3, Attribute.MODIFIABILITY),
    Stakeholder("Аудитор",    4, Attribute.SECURITY),
    Stakeholder("Користувач", 3, Attribute.PERFORMANCE),
]

# Атрибути, які архітектура вже свідомо закрила рішеннями.
covered = {Attribute.COST, Attribute.MODIFIABILITY, Attribute.PERFORMANCE}

# Знаходимо турботи без відповіді — саме тут ховаються майбутні провали.
for s in reg:
    if s.concern not in covered:
        print(f"НЕ ЗАКРИТО: {s.name:<10} (вплив {s.power}) дбає про {ATTR_NAME[s.concern]}")
