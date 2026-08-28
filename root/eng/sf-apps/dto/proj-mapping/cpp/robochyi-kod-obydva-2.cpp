static Status statusFromString(const std::string& s) {
    if (s == "new")       return Status::New;
    if (s == "paid")      return Status::Paid;
    if (s == "shipped")   return Status::Shipped;
    if (s == "cancelled") return Status::Cancelled;
    throw ValidationError("невідомий статус: '" + s + "'");   // митниця сказала «ні»
}

static Line lineFromDto(const LineDto& d) {
    if (d.qty <= 0)
        throw ValidationError("кількість мусить бути > 0, прийшло " +
                              std::to_string(d.qty));
    if (d.sku.empty())
        throw ValidationError("порожній код товару (sku)");
    // Sku(...) сам ще раз перевірить формат — валідні типи бороняться самі
    return Line{ Sku(d.sku), d.qty, Money::fromDouble(d.unitPrice) };
}

Order fromDto(const OrderDto& dto) {
    // 1) Перевіряємо ВСЕ, поки дані ще пласкі й дурні
    if (dto.lines.empty())
        throw ValidationError("замовлення без жодного рядка");

    std::vector<Line> lines;
    lines.reserve(dto.lines.size());
    for (const LineDto& d : dto.lines)
        lines.push_back(lineFromDto(d));      // кожен рядок крізь митницю

    Status status = statusFromString(dto.status);

    // dto.total НЕ довіряємо: домен порахує суму САМ і не дасть її підмінити.
    // Клієнт міг прислати будь-яке число — воно не має влади над інваріантом.

    // 2) Лише тепер будуємо домен — через конструктор, що боронить інваріанти
    return Order::create(OrderId(dto.id), std::move(lines), status);
    //     ^ якщо комбінація полів усе одно нездорова (напр. Shipped без оплати),
    //       конструктор кине САМ — останній рубіж оборони
}
