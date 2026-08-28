// Часткове оновлення: беремо ЖИВЕ замовлення й міняємо тільки надіслане.
// optional-поля кажуть «це поле клієнт справді хотів змінити»,
// а не «тут випадково нуль».
struct OrderPatchDto {
    std::optional<std::string>          status;   // є → міняй статус
    std::optional<std::vector<LineDto>> lines;    // є → заміни рядки
    // чого нема — те не чіпаємо
};

void applyPatch(Order& order, const OrderPatchDto& patch) {
    if (patch.status) {                            // прийшов статус?
        Status s = statusFromString(*patch.status);
        order.changeStatus(s);   // МЕТОД ДОМЕНУ, а не присвоєння поля:
                                 // домен сам вирішить, чи перехід дозволений
    }
    if (patch.lines) {                             // прийшли рядки?
        std::vector<Line> lines;
        for (const LineDto& d : *patch.lines)
            lines.push_back(lineFromDto(d));
        order.replaceLines(std::move(lines));      // теж крізь правило домену
    }
    // status немає в патчі → статус лишився як був. Нічого не знесли.
}
