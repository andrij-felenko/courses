#include <math.h>
// Повна степенева формула ISA (абсолютна висота над рівнем p0):
float altitude_isa_m(float p_hpa, float p0_hpa) {
    const float T0 = 288.15f;      // K
    const float L  = 0.0065f;      // K/m
    return (T0 / L) * (1.0f - powf(p_hpa / p0_hpa, 0.190263f));
}
// Лінійне наближення біля землі (без pow, дешеве):
float altitude_linear_m(float p_hpa, float p0_hpa) {
    return (p0_hpa - p_hpa) * 8.33f;   // 8.33 м на гПа
}
// p = 950, p0 = 1013.25:
//   altitude_isa_m    ≈ 563.0 м
//   altitude_linear_m ≈ 526.9 м   →  недооцінка на ~36 м (6.4%)
