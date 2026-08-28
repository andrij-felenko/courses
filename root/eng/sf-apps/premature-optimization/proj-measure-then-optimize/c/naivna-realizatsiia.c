#include <stdint.h>
#include <stddef.h>
#include <math.h>

// Калібрування конкретного пристрою — визначене на етапі калібрування,
// у пам'яті як змінні. Тому дріб НЕ згортається компілятором у константу.
static int32_t g_offset    = 2048;   // нуль давача, кроки АЦП
static int32_t g_scale_num = 3300;   // чисельник калібрування
static int32_t g_scale_den = 4095;   // знаменник калібрування

// Порахувати RMS струму (в мА) по буферу сирих 12-бітних відліків.
float compute_rms_mA(const uint16_t *raw, size_t n) {
    uint64_t sum_sq = 0;                       // сума квадратів мА
    for (size_t i = 0; i < n; i++) {
        int32_t centered = (int32_t)raw[i] - g_offset;
        int32_t mA = centered * g_scale_num / g_scale_den;   // ← дріб на КОЖЕН відлік
        sum_sq += (uint64_t)((int64_t)mA * mA);
    }
    float mean_sq = (float)sum_sq / (float)n;
    return sqrtf(mean_sq);                      // корінь — ОДИН раз на весь буфер
}
