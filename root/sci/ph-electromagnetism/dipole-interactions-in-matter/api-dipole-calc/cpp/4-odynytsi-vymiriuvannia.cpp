constexpr double debye_to_si(double deb) noexcept {
    return deb * 3.335640951982e-30; // Перетворення Дебай -> C·m
}

constexpr double si_to_debye(double si) noexcept {
    return si / 3.335640951982e-30; // Перетворення C·m -> Дебай
}

constexpr double atomic_to_si(double au) noexcept {
    return au * 8.4783536255e-30;   // Перетворення атомарних одиниць -> C·m
}
