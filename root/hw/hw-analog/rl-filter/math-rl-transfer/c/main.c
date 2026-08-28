// Передавальна функція RL-фільтра нижніх частот на частоті f:
// модуль |H| та фаза (у градусах). Реальна прошивка, не псевдокод.
#include <math.h>

typedef struct { float mag; float phase_deg; } H_t;

H_t rl_lowpass_H(float R, float L, float f) {
    float wt = 2.0f * 3.14159265f * f * (L / R);   // безрозмірне ωτ
    H_t h;
    h.mag       = 1.0f / sqrtf(1.0f + wt * wt);     // 1/√(1+(ωτ)²)
    h.phase_deg = -atanf(wt) * 57.29578f;           // −arctg(ωτ), рад→град
    return h;
}
