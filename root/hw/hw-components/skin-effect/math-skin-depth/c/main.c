// Глибина проникнення δ = sqrt(2·rho / (omega·mu)) — прямо з формули, без сталих-заокруглень.
// Повертає δ у метрах; f — частота в Гц, rho — питомий опір (Ом·м), mu_r — відносна проникність.
#include <math.h>

float skin_depth(float f, float rho, float mu_r) {
    const float MU0 = 1.256637e-6f;    // магнітна стала, Гн/м (4π·10⁻⁷)
    float mu = mu_r * MU0;             // повна проникність металу
    float w  = 2.0f * (float)M_PI * f; // колова частота ω = 2πf
    return sqrtf(2.0f * rho / (w * mu));
}

// Приклад: мідь на 1 МГц.
//   skin_depth(1.0e6f, 1.68e-8f, 1.0f)  ->  ≈ 6.52e-5 м = 65 мкм
