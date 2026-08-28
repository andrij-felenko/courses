#include <math.h>

float rms_level(const int16_t *buf, int n) {
    uint64_t sum_sq = 0;                 // сума квадратів; 64 біти проти переповнення
    for (int i = 0; i < n; i++) {
        int32_t s = buf[i];
        sum_sq += (uint64_t)(s * s);     // s*s ≤ 32768² ≈ 1.07·10⁹ — влазить у int32
    }
    float mean_sq = (float)sum_sq / (float)n;
    return sqrtf(mean_sq);               // 0 .. 32767
}
