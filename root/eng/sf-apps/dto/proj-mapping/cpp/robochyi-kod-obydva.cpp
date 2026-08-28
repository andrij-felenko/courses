// Єдина відповідність enum ⇄ рядок — в одному місці на обидва напрями
static std::string statusToString(Status s) {
    switch (s) {
        case Status::New:       return "new";
        case Status::Paid:      return "paid";
        case Status::Shipped:   return "shipped";
        case Status::Cancelled: return "cancelled";
    }
    // жодного default: щойно додаси стан у enum — компілятор
    // (з -Wswitch) нагадає дописати переклад тут, а не мовчки збреше
    throw std::logic_error("невідомий Status у statusToString");
}

// Маленький маппер для вкладеного рядка — своя дрібна відповідальність
static LineDto lineToDto(const Line& l) {
    return LineDto{
        l.sku.str(),               // Sku → голий рядок: тип роздягається на межі
        l.qty,
        l.unitPrice.toDouble()     // Money → double: свідома втрата типу-грошей
    };
}

OrderDto toDto(const Order& order) {
    OrderDto dto;
    dto.id     = order.id().value();          // OrderId → long
    dto.total  = order.total().toDouble();    // ПРАВИЛО, не сире поле: рахуємо
    dto.status = statusToString(order.status());
    // cost_ навмисно НЕ їде — рішення дизайну, втілене мовчанням

    dto.lines.reserve(order.lines().size());
    for (const Line& l : order.lines())
        dto.lines.push_back(lineToDto(l));
    return dto;
}
