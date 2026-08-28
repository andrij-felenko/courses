#include <math.h>

// Добротність і смуга послідовного контуру на його f0.
// L у генрі, C у фарадах, R — повний послідовний опір втрат (Ом).
typedef struct { float f0, Q, bw; } Resonance;

Resonance series_resonance(float L, float C, float R)
{
    Resonance r;
    r.f0 = 1.0f / (2.0f * (float)M_PI * sqrtf(L * C));
    float XL = 2.0f * (float)M_PI * r.f0 * L;   // = Xc на резонансі
    r.Q  = XL / R;                              // добротність
    r.bw = r.f0 / r.Q;                          // смуга −3 дБ
    return r;
}
// series_resonance(100e-6f, 250e-12f, 12.0f) -> f0≈1 МГц, Q≈52, bw≈19 кГц
