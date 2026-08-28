from dataclasses import dataclass, field

@dataclass
class LineDto:
    sku: str                        # тут уже голий рядок — DTO «дурний»
    qty: int
    unit_price: float               # гроші як float — на межі так буває

@dataclass
class OrderDto:
    id: int
    total: float                    # готовий результат, не собівартість
    status: str                     # "new" / "paid" / "shipped" / "cancelled"
    lines: list[LineDto] = field(default_factory=list)
