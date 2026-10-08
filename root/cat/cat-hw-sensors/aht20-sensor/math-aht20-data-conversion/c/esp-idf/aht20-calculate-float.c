#include <stdint.h>

// Обчислення з плаваючою крапкою (використовує FPU за наявності)
void aht20_calculate_float(uint32_t s_rh, uint32_t s_t, float *rh_pct, float *temp_c) {
    if (rh_pct) {
        *rh_pct = ((float)s_rh * 100.0f) / 1048576.0f;
    }
    if (temp_c) {
        *temp_c = ((float)s_t * 200.0f) / 1048576.0f - 50.0f;
    }
}

// Безпечне цілочисельне обчислення з фіксованою крапкою (соті частки: 2550 = 25.50)
void aht20_calculate_fixed(uint32_t s_rh, uint32_t s_t, int32_t *rh_x100, int32_t *temp_x100) {
    if (rh_x100) {
        // Приведення до uint64_t запобігає переповненню 32-бітного цілого
        *rh_x100 = (int32_t)(((uint64_t)s_rh * 10000ULL) >> 20);
    }
    if (temp_x100) {
        // 200 * 100 = 20000 для сотих часток градуса, зміщення 50 * 100 = 5000
        *temp_x100 = (int32_t)((((uint64_t)s_t * 20000ULL) >> 20) - 5000);
    }
}
