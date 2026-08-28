#include <stdint.h>
#include <stddef.h>
#include <math.h>

static int32_t g_offset = 2048;
// Готуємо обернене ОДИН раз при зміні калібрування, а не в гарячому циклі.
static int64_t g_recip  = 0;      // (SCALE_NUM << Q) / SCALE_DEN
#define RECIP_Q  32

void set_calibration(int32_t offset, int32_t scale_num, int32_t scale_den) {
    g_offset = offset;
    // Єдиний поділ на весь час життя цього калібрування:
    g_recip  = ((int64_t)scale_num << RECIP_Q) / scale_den;
}

float compute_rms_mA_fast(const uint16_t *raw, size_t n) {
    uint64_t sum_sq = 0;
    for (size_t i = 0; i < n; i++) {
        int32_t centered = (int32_t)raw[i] - g_offset;
        // Замість ділення — множення на обернене й зсув. Обидва по 1 такту.
        int32_t mA = (int32_t)(((int64_t)centered * g_recip) >> RECIP_Q);
        sum_sq += (uint64_t)((int64_t)mA * mA);
    }
    float mean_sq = (float)sum_sq / (float)n;
    return sqrtf(mean_sq);
}
