#include <stdint.h>
#include <math.h>

typedef struct { double t, volt, curr; } BatSample;   // час, напруга, струм (з BAT)

// Оцінити внутрішній опір із двох точок: сталого й пікового струму.
// ΔV / ΔI ≈ R_вн (бо V = V_хім − I·R_вн, а V_хім за короткий час майже стала).
static double est_resistance(const BatSample *s, int n) {
    double v_lo = 0, i_lo = 1e9, v_hi = 0, i_hi = 0;
    for (int k = 0; k < n; k++) {
        if (s[k].curr < i_lo) { i_lo = s[k].curr; v_lo = s[k].volt; } // спокій
        if (s[k].curr > i_hi) { i_hi = s[k].curr; v_hi = s[k].volt; } // пік
    }
    if (i_hi - i_lo < 1.0) return 0.0;             // струм майже не мінявся — не оцінити
    return (v_lo - v_hi) / (i_hi - i_lo);          // ΔV/ΔI, Ом
}
