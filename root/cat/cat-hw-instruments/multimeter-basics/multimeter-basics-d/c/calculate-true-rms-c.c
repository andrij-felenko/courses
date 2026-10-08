#include <math.h>
#include <stddef.h>
#include <stdint.h>

// Обчислення True RMS за масивом дискретних відліків АЦП
float calculate_true_rms_c(const int16_t *samples, size_t sample_count, float scale_factor) {
    if (sample_count == 0) return 0.0f;

    double sum_squares = 0.0;
    for (size_t i = 0; i < sample_count; ++i) {
        float voltage = (float)samples[i] * scale_factor;
        sum_squares += (double)(voltage * voltage);
    }

    double mean_square = sum_squares / (double)sample_count;
    return (float)sqrt(mean_square);
}
