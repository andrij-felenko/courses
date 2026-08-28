#include <math.h>

// Скільки лінія «повзе» від 0 до порога (0.7·Vcc) при підтяжці R_p і ємності C.
// Саме цей час, а не спад, ставить стелю частоти open-drain шини.
static float rise_to_threshold_s(float rp_ohm, float c_farad, float thr_frac) {
    // V(t)=Vcc(1−e^{−t/τ});  t = −τ·ln(1−thr)
    float tau = rp_ohm * c_farad;
    return -tau * logf(1.0f - thr_frac);   // thr_frac = 0.7 → ≈1.20·τ
}
// Приклад I2C: R_p = 4.7 кОм, C = 200 пФ (помірна шина), поріг 0.7.
//   τ = 4700 · 200e-12 = 9.4e-7 с = 0.94 мкс
//   t = 1.20 · 0.94 мкс ≈ 1.13 мкс
