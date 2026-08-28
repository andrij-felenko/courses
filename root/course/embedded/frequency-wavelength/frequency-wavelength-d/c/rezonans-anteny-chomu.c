#include <math.h>

// Фізична довжина чвертьхвильового штиря з поправкою на реальність.
// f_hz — частота; k — сумарний коефіцієнт укорочення (≈0.95 для тонкого дроту).
float quarter_wave_len_m(float f_hz, float k) {
    const float c = 2.998e8f;
    float lambda0 = c / f_hz;
    return lambda0 * 0.25f * k;
}

// 868 МГц → ≈0.082 м (8.2 см), а не наївні 8.6 см
