// Мінімальний час вибірки для заряду конденсатора SAR-АЦП до ½ LSB.
// Вхід: опір джерела+ключа (Ом), ємність вибірки (Ф), розрядність, частота такту АЦП (Гц).
// Повертає потрібне число тактів вибірки (округлене вгору).
#include <math.h>
#include <stdint.h>

uint32_t sample_clocks(float r_ohm, float c_farad, uint8_t bits, float adc_hz) {
    float tau      = r_ohm * c_farad;          // стала часу вхідного кола
    float n_tau    = (float)bits * 0.6931f;    // ln(2^bits) = bits·ln2
    float t_sample = (n_tau + 1.0f) * tau;     // +1 τ запасу
    float clocks   = t_sample * adc_hz;        // час → такти
    return (uint32_t)ceilf(clocks);
}

// Приклад: R=1 кОм, C=4 пФ, 12 біт, такт АЦП 20 МГц
uint32_t n = sample_clocks(1000.0f, 4e-12f, 12, 20e6f);  // ≈ 1 такт (округлено вгору)
