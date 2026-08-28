inline double dipole_debye_to_si(double deb) {
    return deb * 3.335640951982e-30; // Перетворення Дебай -> C·m
}

inline double dipole_si_to_debye(double si) {
    return si / 3.335640951982e-30; // Перетворення C·m -> Дебай
}

inline double dipole_atomic_to_si(double au) {
    return au * 8.4783536255e-30;   // Перетворення атомарних одиниць -> C·m
}
