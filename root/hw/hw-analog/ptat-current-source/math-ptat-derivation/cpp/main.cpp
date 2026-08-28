#include <cmath>

// Тепловий потенціал U_T = k*T/q при абсолютній температурі T (К), у вольтах.
float thermal_voltage(float T_kelvin)
{
    const float k = 1.380649e-23f;   // стала Больцмана, Дж/К
    const float q = 1.602177e-19f;   // елементарний заряд, Кл
    return k * T_kelvin / q;
}

// Різниця падінь база-емітер двох переходів із відношенням площ N.
// ΔU_BE = U_T*ln(N) — чистий PTAT, лінійний крізь нуль.
float delta_vbe(float T_kelvin, float N)
{
    return thermal_voltage(T_kelvin) * std::log(N);   // ∝ T
}

// Нахил d(ΔU_BE)/dT = (k/q)*ln(N) — стала, та сама при будь-якій T.
float delta_vbe_slope(float N)
{
    const float k_over_q = 8.617333e-5f;          // В/К
    return k_over_q * std::log(N);                  // ≈ 0.1792 мВ/К для N=8
}

// delta_vbe(233.15f, 8.0f) -> ~41.8 мВ   (−40 °C)
// delta_vbe(398.15f, 8.0f) -> ~71.3 мВ   (+125 °C)
// Перевірка лінійності: (71.3 − 41.8) / (398.15 − 233.15) = 0.1792 мВ/К — той самий нахил.
