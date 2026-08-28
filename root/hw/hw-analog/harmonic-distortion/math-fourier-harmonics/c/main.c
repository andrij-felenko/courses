#include <math.h>

// amp[0] — основна (1-ша гармоніка), amp[1..] — 2-га, 3-тя, ...
// n — скільки всього елементів у масиві (основна + гармоніки)
float thd_from_harmonics(const float *amp, int n)
{
    float fund = amp[0];                 // основна гармоніка, U₁
    if (fund <= 0.0f) return 0.0f;       // немає сигналу — THD не визначений

    float sum_sq = 0.0f;                 // сума квадратів вищих гармонік
    for (int k = 1; k < n; ++k)          // від 2-ї (індекс 1) і вище
        sum_sq += amp[k] * amp[k];       // U₂² + U₃² + ...

    return sqrtf(sum_sq) / fund;         // √(ΣUₙ²) / U₁  — частка
}

void demo(void)
{
    // основна 1.000 В; гармоніки 2..7 (типовий спадний «хвіст»)
    float amp[7] = { 1.000f, 0.0120f, 0.0050f, 0.0020f,
                     0.0011f, 0.0006f, 0.0003f };

    float thd     = thd_from_harmonics(amp, 7);   // √(1.2e-4+2.5e-5+...) /1.0
    float thd_pct = thd * 100.0f;                 // у відсотках
    float thd_db  = 20.0f * log10f(thd);          // у децибелах

    // thd     ≈ 0.0132  (корінь із суми ≈ 0.0132 В при основній 1.000 В)
    // thd_pct ≈ 1.32 %
    // thd_db  ≈ −37.6 dB
    (void)thd_pct; (void)thd_db;
}
