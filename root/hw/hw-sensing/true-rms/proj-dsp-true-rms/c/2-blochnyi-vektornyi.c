#include <math.h>
#include <stddef.h>

// Блочний розрахунок True RMS з усуненням постійної складової
// buffer: масив напруг у вольтах, зібраний за цілу кількість періодів
float calculate_true_rms_block(const float *buffer, size_t length) {
    if (buffer == NULL || length == 0) return 0.0f;

    // 1. Швидкий перший прохід: точне середнє значення (DC offset)
    float sum_dc0 = 0.0f, sum_dc1 = 0.0f, sum_dc2 = 0.0f, sum_dc3 = 0.0f;
    size_t i = 0;
    for (; i + 3 < length; i += 4) {
        sum_dc0 += buffer[i + 0];
        sum_dc1 += buffer[i + 1];
        sum_dc2 += buffer[i + 2];
        sum_dc3 += buffer[i + 3];
    }
    float sum_dc = (sum_dc0 + sum_dc1) + (sum_dc2 + sum_dc3);
    for (; i < length; ++i) {
        sum_dc += buffer[i];
    }
    float dc_mean = sum_dc / (float)length;

    // 2. Другий прохід: накопичення квадратів змінної складової (v[i] - dc_mean)
    float sum_sq0 = 0.0f, sum_sq1 = 0.0f, sum_sq2 = 0.0f, sum_sq3 = 0.0f;
    i = 0;
    for (; i + 3 < length; i += 4) {
        float d0 = buffer[i + 0] - dc_mean;
        float d1 = buffer[i + 1] - dc_mean;
        float d2 = buffer[i + 2] - dc_mean;
        float d3 = buffer[i + 3] - dc_mean;

        sum_sq0 += d0 * d0;
        sum_sq1 += d1 * d1;
        sum_sq2 += d2 * d2;
        sum_sq3 += d3 * d3;
    }
    float total_sq = (sum_sq0 + sum_sq1) + (sum_sq2 + sum_sq3);
    for (; i < length; ++i) {
        float d = buffer[i] - dc_mean;
        total_sq += d * d;
    }

    return sqrtf(total_sq / (float)length);
}
