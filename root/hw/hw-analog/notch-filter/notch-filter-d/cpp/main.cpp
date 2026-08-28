#include <numbers>

// Розрахунок twin-T режектора під задану частоту-ціль.
// Задаємо ємність бічних конденсаторів C (Ф); повертаємо
// бічний резистор R (Ом). Шунти: R_shunt = R/2, C_shunt = 2*C.
float twint_R_from_f0(float f0_hz, float c_side_f)
{
    return 1.0f / (2.0f * std::numbers::pi_v<float> * f0_hz * c_side_f);
}

// Зворотна перевірка: яка частота провалу вийде на цих R, C.
float twint_f0(float r_side_ohm, float c_side_f)
{
    return 1.0f / (2.0f * std::numbers::pi_v<float> * r_side_ohm * c_side_f);
}
// twint_R_from_f0(50.0f, 100e-9f) -> ~31831 Ом
// twint_f0(31830.0f, 100e-9f)     -> ~50.0 Гц  ✓
