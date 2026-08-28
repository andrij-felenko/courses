#include <cstdint>

// Таблиця істинності функції 3 змінних (2^3 = 8 біт)
using TruthTable8 = uint8_t;

// Операція AND двох формул - одна інструкція CPU:
TruthTable8 f_and(TruthTable8 f1, TruthTable8 f2) {
    return f1 & f2;
}

// Операція OR двох формул:
TruthTable8 f_or(TruthTable8 f1, TruthTable8 f2) {
    return f1 | f2;
}

// Операція NOT:
TruthTable8 f_not(TruthTable8 f1) {
    return ~f1;
}
