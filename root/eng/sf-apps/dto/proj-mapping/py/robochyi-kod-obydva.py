# Єдина відповідність enum ⇄ рядок — в одному місці на обидва напрями
_STATUS_TO_STR = {
    Status.NEW:       "new",
    Status.PAID:      "paid",
    Status.SHIPPED:   "shipped",
    Status.CANCELLED: "cancelled",
}

def status_to_string(s: Status) -> str:
    try:
        return _STATUS_TO_STR[s]
    except KeyError:
        # щойно додаси стан у enum, а сюди ні — впаде голосно тут,
        # а не мовчки поверне порожнечу
        raise ValueError(f"невідомий Status у status_to_string: {s}")

# Маленький маппер для вкладеного рядка — своя дрібна відповідальність
def line_to_dto(l: Line) -> LineDto:
    return LineDto(
        sku=l.sku.str(),               # Sku → голий рядок: тип роздягається на межі
        qty=l.qty,
        unit_price=l.unit_price.to_float(),  # Money → float: свідома втрата типу-грошей
    )

def to_dto(order: Order) -> OrderDto:
    return OrderDto(
        id=order.id.value,                     # OrderId → int
        total=order.total().to_float(),        # ПРАВИЛО, не сире поле: рахуємо
        status=status_to_string(order.status),
        # cost навмисно НЕ їде — рішення дизайну, втілене мовчанням
        lines=[line_to_dto(l) for l in order.lines],
    )
