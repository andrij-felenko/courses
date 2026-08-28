#include <cmath>
#include <complex>

using cplx = std::complex<double>;

constexpr double K_BOLTZ = 1.380649e-23;
constexpr double T0      = 290.0;
constexpr double FOUR_KT = 4.0 * K_BOLTZ * T0;   // 4kT₀ ≈ 1.6e-20

struct NoiseParams { double Fmin, Rn, Gopt, Bopt; };

// З двох вхідних джерел (en, in) та їх кореляції c — чотири шумові параметри.
// en у В/√Гц, in у А/√Гц, c безрозмірний комплексний (|c| ≤ 1).
NoiseParams noise_params(double en, double in_, cplx c) {
    double en2 = en * en;                 // ⟨|en|²⟩  (густина потужності напруги)
    double in2 = in_ * in_;               // ⟨|in|²⟩  (густина потужності струму)

    double Rn = en2 / FOUR_KT;            // шумовий опір з напруги

    // провідність кореляції: Yc = c · (in/en)  (відношення модулів × фаза c)
    cplx Yc = c * (in_ / en);
    double Gc = Yc.real(), Bc = Yc.imag();

    // некорельована частка струму: потужність × (1 − |c|²) → провідність Gu
    double in2_uncorr = in2 * (1.0 - std::norm(c));
    double Gu = in2_uncorr / FOUR_KT;

    NoiseParams p;
    p.Bopt = -Bc;                                 // компенсуємо реактивну кореляцію
    p.Gopt = std::sqrt(Gc*Gc + Gu / Rn);          // геометричне серединне двох механізмів
    p.Fmin = 1.0 + 2.0 * Rn * (p.Gopt + Gc);      // дно чаші (у разах)
    p.Rn   = Rn;
    return p;
}

// виклик:
double en = 0.45e-9;                      // 0.45 нВ/√Гц
double in_ = 4.0e-12;                     // 4.0 пА/√Гц
cplx c{0.2, 0.3};                         // кореляція
NoiseParams p = noise_params(en, in_, c);
// p.Rn ≈ 12.6 Ом
// p.Gopt ≈ 8.48 мСм,  p.Bopt ≈ −2.67 мСм   →  Yopt ≈ (8.48 − j2.67) мСм
// p.Fmin ≈ 1.259 разів  →  10·log10 ≈ 1.00 дБ
