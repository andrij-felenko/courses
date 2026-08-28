from dataclasses import dataclass, field

# Усередині — багатий домен з поведінкою і прихованими полями
class Order:
    def __init__(self, id, cost, lines, status):
        self._id = id            # внутрішній ключ бази — назовні не потрібен
        self._cost = cost        # собівартість — комерційна таємниця
        self._lines = lines
        self._status = status

    def total(self) -> Money:    # правило: як рахується сума
        ...
    def cancel(self) -> None:    # правило: коли можна скасувати
        ...
    # ... інваріанти, що бережуть коректність

# На межі — пласка виписка: лише те, що клієнт має право й потребу бачити
@dataclass
class OrderDto:
    id: int
    total: float              # порахований результат, не собівартість
    status: str
    lines: list[LineDto] = field(default_factory=list)
