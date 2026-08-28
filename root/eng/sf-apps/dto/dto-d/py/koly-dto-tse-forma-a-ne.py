from dataclasses import dataclass

# frozen=True: поля не можна переприсвоїти після створення.
# Хочеш інше значення — dataclasses.replace(dto, total=...) робить НОВИЙ.
@dataclass(frozen=True)
class OrderDto:
    id: int
    total: float
    status: str
    lines: tuple["LineDto", ...] = ()   # tuple, не list — вкладене теж застигле

# Дві копії з однаковими полями — рівні й взаємозамінні: тотожності нема.
a = OrderDto(42, 100.0, "paid")
b = OrderDto(42, 100.0, "paid")
assert a == b        # рівність за значенням полів, не за «котрий об'єкт»
