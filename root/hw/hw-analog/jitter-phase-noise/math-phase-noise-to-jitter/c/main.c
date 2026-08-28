#include <math.h>

// Одна горизонтальна ділянка маски фазового шуму.
typedef struct {
    float f_lo, f_hi;   // межі відступу, Гц
    float L_dbc;        // рівень L(f) на ділянці, дБн/Гц
} PnSegment;

// Інтегрований RMS-джиттер у секундах за кусково-плоскою маскою.
// f0 — несуча, Гц;  seg/n — ділянки маски в робочій смузі.
float integrated_jitter_s(float f0, const PnSegment *seg, int n) {
    double var_phi = 0.0;                       // дисперсія фази, рад²
    for (int i = 0; i < n; ++i) {
        double dens  = pow(10.0, seg[i].L_dbc / 10.0);   // дБн/Гц → рази
        double width = seg[i].f_hi - seg[i].f_lo;        // ширина ділянки, Гц
        var_phi += dens * width;                         // площа прямокутника
    }
    var_phi *= 2.0;                             // однобічна L → повна щільність фази
    double sigma_phi = sqrt(var_phi);           // RMS фази, рад
    return (float)(sigma_phi / (2.0 * M_PI * f0));       // → секунди
}

// Маска нашого джерела 100 МГц у смузі 12 кГц…20 МГц.
PnSegment mask[] = {
    { 12.0e3f,  100.0e3f, -120.0f },
    { 100.0e3f,   1.0e6f, -135.0f },
    {   1.0e6f,  20.0e6f, -150.0f },
};

float f0  = 100.0e6f;
float tj  = integrated_jitter_s(f0, mask, 3);
// var_phi(до×2) = 1e-12·88e3 + 3.162e-14·900e3 + 1e-15·19e6
//              = 8.80e-8 + 2.85e-8 + 1.90e-8 = 1.355e-7
// ×2 = 2.710e-7 рад²;  √ = 5.206e-4 рад;  /(2π·1e8) = 8.29e-13 с ≈ 0.83 пс
