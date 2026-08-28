#include <cstdio>

// Кожна одиниця — окрема структура-обгортка над double. Усередині
// однакове число; різними їх робить тип — і компілятор.
struct NewtonSeconds     { double v; };
struct PoundForceSeconds  { double v; };

// Єдиний дозволений місток — явний перевід із коефіцієнтом.
constexpr NewtonSeconds to_ns(PoundForceSeconds x) {
    return NewtonSeconds{ x.v * 4.448222 };
}

// Навігація приймає ЛИШЕ ньютон-секунди — це записано в типі аргументу.
void apply_impulse(NewtonSeconds j) {
    (void)j.v;   // ... коригуємо траєкторію, знаючи, що j — точно в Н·с ...
}

int main() {
    // apply_impulse(PoundForceSeconds{1.85});   // ← НЕ КОМПІЛЮЄТЬСЯ:
    //   cannot convert 'PoundForceSeconds' to 'NewtonSeconds'
    apply_impulse(to_ns(PoundForceSeconds{1.85}));  // ✓ перевід явний
    apply_impulse(NewtonSeconds{8.23});             // ✓ вже в Н·с
}
