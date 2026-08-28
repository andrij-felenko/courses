// notch на f0 за частоти дискретизації fs і добротності Q → коеф. біквада
#include <cmath>

struct Biquad { float b0, b1, b2, a1, a2; };  // вже нормовані на a0

Biquad design_notch(float f0, float fs, float Q) {
    const float w0    = 2.0f * static_cast<float>(M_PI) * f0 / fs;  // 2π·50/1000 ≈ 0.3142 рад/відлік
    const float cosw0 = std::cos(w0);
    const float alpha = std::sin(w0) / (2.0f * Q);  // sin(w0)/(2·12.5) — задає ширину

    const float a0 = 1.0f + alpha;                  // спільний знаменник
    Biquad bq;
    bq.b0 = 1.0f          / a0;                     // у чисельнику: s² + 1
    bq.b1 = (-2.0f*cosw0) / a0;
    bq.b2 = 1.0f          / a0;
    bq.a1 = (-2.0f*cosw0) / a0;                     // зворотний зв'язок
    bq.a2 = (1.0f - alpha)/ a0;
    return bq;                                      // b1 == a1 — прикмета саме notch
}
