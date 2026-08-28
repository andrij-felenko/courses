# Контекст БУХГАЛТЕРІЇ: юзер — це платник за рахунками
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Payer:
    id: str
    name: str
    tax_id: str        # не None: без ІПН платника немає
    credit_limit: float
    iban: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"\d{8,10}", self.tax_id):
            raise ValueError("ІПН має бути 8–10 цифр")
    # Жодного stage, probability — бухгалтерії байдуже до воронки.
