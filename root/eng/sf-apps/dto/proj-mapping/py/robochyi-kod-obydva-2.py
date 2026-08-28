_STATUS_FROM_STR = {
    "new":       Status.NEW,
    "paid":      Status.PAID,
    "shipped":   Status.SHIPPED,
    "cancelled": Status.CANCELLED,
}

def status_from_string(s: str) -> Status:
    try:
        return _STATUS_FROM_STR[s]
    except KeyError:
        raise ValidationError(f"невідомий статус: '{s}'")   # митниця сказала «ні»

def line_from_dto(d: LineDto) -> Line:
    if d.qty <= 0:
        raise ValidationError(f"кількість мусить бути > 0, прийшло {d.qty}")
    if not d.sku:
        raise ValidationError("порожній код товару (sku)")
    # Sku(...) сам ще раз перевірить формат — валідні типи бороняться самі
    return Line(Sku(d.sku), d.qty, Money.from_float(d.unit_price))

def from_dto(dto: OrderDto) -> Order:
    # 1) Перевіряємо ВСЕ, поки дані ще пласкі й дурні
    if not dto.lines:
        raise ValidationError("замовлення без жодного рядка")

    lines = [line_from_dto(d) for d in dto.lines]   # кожен рядок крізь митницю

    status = status_from_string(dto.status)

    # dto.total НЕ довіряємо: домен порахує суму САМ і не дасть її підмінити.
    # Клієнт міг прислати будь-яке число — воно не має влади над інваріантом.

    # 2) Лише тепер будуємо домен — через конструктор, що боронить інваріанти
    return Order.create(OrderId(dto.id), lines, status)
    #      ^ якщо комбінація полів усе одно нездорова (напр. Shipped без оплати),
    #        конструктор кине САМ — останній рубіж оборони
