# Контекст ПРОДАЖІВ: юзер — це наводка на угоду
from dataclasses import dataclass
from typing import Literal

Stage = Literal["new", "qualified", "won", "lost"]

@dataclass(frozen=True)
class Lead:
    id: str
    name: str
    stage: Stage        # не None!
    probability: float  # не None!
    owner_id: str       # не None!

    def __post_init__(self) -> None:
        if not 0 <= self.probability <= 1:
            raise ValueError("ймовірність поза [0, 1]")
    # валідність тепер вбудована: ліда без стадії просто не існує.
    # Жодного tax_id, iban — цей світ про них не чув.
