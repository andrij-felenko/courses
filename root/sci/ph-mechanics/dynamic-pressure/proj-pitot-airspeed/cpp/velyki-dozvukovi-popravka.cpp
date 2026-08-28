#include <math.h>

// Справжня швидкість зі стисливою поправкою (дозвукове гальмування, γ=1.4).
// M² = 5·[(Δp/p + 1)^(2/7) − 1];  TAS = M·√(γRT).
float tas_compressible(float dp, float p_static, float T_kelvin) {
    if (dp <= 0.0f) return 0.0f;
    float m2 = 5.0f * (powf(dp / p_static + 1.0f, 2.0f / 7.0f) - 1.0f);
    float a  = sqrtf(GAMMA * R_AIR * T_kelvin);      // місцева швидкість звуку
    return sqrtf(m2) * a;                            // TAS = M·a
}
