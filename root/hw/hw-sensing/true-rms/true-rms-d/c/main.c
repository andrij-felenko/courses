#include <math.h>
#include <stddef.h>
#include <stdbool.h>

// Високопродуктивний блочний розрахунок True RMS з усуненням зміщення нуля
// samples: буфер напруг у вольтах, зібраний строго за ціле число періодів
float calculate_true_rms(const float *samples, size_t length) {
    if (samples == NULL || length == 0) {
        return 0.0f;
    }

    // 1. Перший прохід: обчислення точного середнього постійного зміщення (DC Offset)
    // Цикл розгорнуто на 4 незалежні акумулятори для завантаження конвеєра FPU
    float sum_dc0 = 0.0f, sum_dc1 = 0.0f, sum_dc2 = 0.0f, sum_dc3 = 0.0f;
    size_t i = 0;
    for (; i + 3 < length; i += 4) {
        sum_dc0 += samples[i + 0];
        sum_dc1 += samples[i + 1];
        sum_dc2 += samples[i + 2];
        sum_dc3 += samples[i + 3];
    }
    float sum_dc = (sum_dc0 + sum_dc1) + (sum_dc2 + sum_dc3);
    for (; i < length; ++i) {
        sum_dc += samples[i];
    }
    const float dc_offset = sum_dc / (float)length;

    // 2. Другий прохід: накопичення квадратів змінної складової
    float sum_sq0 = 0.0f, sum_sq1 = 0.0f, sum_sq2 = 0.0f, sum_sq3 = 0.0f;
    i = 0;
    for (; i + 3 < length; i += 4) {
        float d0 = samples[i + 0] - dc_offset;
        float d1 = samples[i + 1] - dc_offset;
        float d2 = samples[i + 2] - dc_offset;
        float d3 = samples[i + 3] - dc_offset;

        sum_sq0 += d0 * d0;
        sum_sq1 += d1 * d1;
        sum_sq2 += d2 * d2;
        sum_sq3 += d3 * d3;
    }
    float total_sq = (sum_sq0 + sum_sq1) + (sum_sq2 + sum_sq3);
    for (; i < length; ++i) {
        float d = samples[i] - dc_offset;
        total_sq += d * d;
    }

    // 3. Добування кореня з середнього квадрата
    return sqrtf(total_sq / (float)length);
}
