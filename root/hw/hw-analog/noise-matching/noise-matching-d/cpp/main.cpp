#include <cmath>
#include <complex>

using cplx = std::complex<float>;

// Коефіцієнт шуму за провідністю джерела (формула Роте — Дальке).
// Fmin задано в РАЗАХ (не дБ); провідності — у сименсах.
float noise_factor(float Fmin, float Rn, cplx Yopt, cplx Ys) {
    float Gs = Ys.real();                   // дійсна частина провідності джерела
    cplx d = Ys - Yopt;                     // відхід від оптимуму
    float dist2 = std::norm(d);             // |Ys − Yopt|²
    return Fmin + (Rn / Gs) * dist2;
}

// 0.6 дБ у разах:  10^(0.6/10) = 1.148
float Fmin = 1.148f;
float Rn   = 30.0f;
cplx Yopt{ 8e-3f, -6e-3f};                  // (8 − j6) мСм
cplx Ys  {12e-3f, -2e-3f};                  // (12 − j2) мСм

float F  = noise_factor(Fmin, Rn, Yopt, Ys);  // ≈ 1.228 (разів)
float dB = 10.0f * std::log10(F);              // ≈ 0.89 дБ
