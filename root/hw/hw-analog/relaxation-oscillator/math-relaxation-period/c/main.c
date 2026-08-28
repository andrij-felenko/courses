// Період і резистор релаксаційного генератора з порогами 1/3 і 2/3 живлення.
// τ = R·C; кожна фаза = τ·ln2; період = 2·τ·ln2.
#include <math.h>

float relax_period(float r_ohm, float c_farad)  // період T, секунди
{
    const float LN2 = 0.6931472f;
    return 2.0f * r_ohm * c_farad * LN2;         // T = 2·R·C·ln2 ≈ 1.386·R·C
}

float relax_resistor(float f_hz, float c_farad)  // R під бажану частоту
{
    const float K = 1.386294f;                   // 2·ln2
    return 1.0f / (K * f_hz * c_farad);          // R = 1 / (2·ln2 · f · C)
}

// Приклад: 2 Гц при 1 мкФ
float R = relax_resistor(2.0f, 1.0e-6f);         // ≈ 360 700 Ом → ставимо 360 кОм
