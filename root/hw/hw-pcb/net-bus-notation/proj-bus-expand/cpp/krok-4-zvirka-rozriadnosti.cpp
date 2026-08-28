// Чи можна стикувати дві шини? Лише якщо однакова розрядність.
static bool widths_match(const BusName& a, const BusName& b) {
    return bus_width(a) == bus_width(b);
}

// Сумарна ширина склеювання {частина, частина, ...}.
// {CTRL, D[6..0]} → 1 + 7 = 8.
static int concat_width(const std::vector<BusName>& parts) {
    int total = 0;
    for (const auto& p : parts) total += bus_width(p);
    return total;
}

// Звірити склеювання з приймачем заданої ширини; інакше — попередити.
static bool check_concat(const std::vector<BusName>& parts, int sink_width) {
    int w = concat_width(parts);
    if (w != sink_width) {
        printf("ПОМИЛКА розрядності: склеювання дає %d ліній, приймач чекає %d\n",
               w, sink_width);
        return false;
    }
    return true;
}
