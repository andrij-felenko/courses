from dataclasses import dataclass
from typing import Optional

# Вихід: усе присутнє, обчислене, тільки для читання
@dataclass(frozen=True)
class OrderResponse:
    id: int               # сервер завжди знає id
    total: float          # ПОРАХОВАНО доменом
    status: str
    lines: list["LineView"]

# Вхід на СТВОРЕННЯ: id ще нема, total слати НЕ можна
@dataclass(frozen=True)
class CreateOrderRequest:
    lines: list["LineInput"]   # самий намір; більш нічого клієнт не диктує
    # жодного id, жодного total — їх дасть/порахує сервер

# Вхід на РЕДАГУВАННЯ: усе optional — «прийшло тільки те, що міняємо»
@dataclass(frozen=True)
class PatchOrderRequest:
    status: Optional[str] = None   # є → зміни; None → не чіпай
    lines: Optional[list["LineInput"]] = None
