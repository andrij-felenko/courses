// RL-фільтр нижніх частот: підбір L за частотою зламу
// і перевірка послаблення на частоті завади. Реальна прошивка-калькулятор.
#include <math.h>

float rl_inductance(float R, float fc) {       // потрібна L з f꜀ = R/(2πL)
    return R / (2.0f * 3.14159265f * fc);      // у генрі
}

// Частка амплітуди, що проходить крізь ФНЧ на частоті f:  R / √(R² + (ωL)²)
float rl_lowpass_gain(float R, float L, float f) {
    float XL = 2.0f * 3.14159265f * f * L;     // реактивний опір котушки на f
    return R / sqrtf(R * R + XL * XL);         // 1.0 у смузі, →0 високо
}
