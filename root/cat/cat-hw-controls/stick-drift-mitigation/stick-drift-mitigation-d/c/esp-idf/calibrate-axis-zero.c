#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CALIB_SAMPLE_COUNT 64

typedef struct {
    uint16_t raw_zero;
    uint16_t raw_min;
    uint16_t raw_max;
    float scale_neg;
    float scale_pos;
    bool is_calibrated;
} axis_calib_t;

bool calibrate_axis_zero(axis_calib_t *calib, const uint16_t *samples, float max_allowed_variance) {
    uint32_t sum = 0;
    for (int i = 0; i < CALIB_SAMPLE_COUNT; i++) {
        sum += samples[i];
    }
    float mean = (float)sum / CALIB_SAMPLE_COUNT;

    float variance = 0.0f;
    for (int i = 0; i < CALIB_SAMPLE_COUNT; i++) {
        float diff = (float)samples[i] - mean;
        variance += diff * diff;
    }
    variance /= CALIB_SAMPLE_COUNT;

    if (variance > max_allowed_variance) {
        return false; // Відхилення через наявність руху важеля
    }

    calib->raw_zero = (uint16_t)roundf(mean);
    if (calib->raw_zero > calib->raw_min && calib->raw_max > calib->raw_zero) {
        calib->scale_neg = 1.0f / (float)(calib->raw_zero - calib->raw_min);
        calib->scale_pos = 1.0f / (float)(calib->raw_max - calib->raw_zero);
        calib->is_calibrated = true;
    }
    return calib->is_calibrated;
}

float normalize_axis_value(const axis_calib_t *calib, uint16_t raw_val) {
    if (!calib->is_calibrated) {
        return 0.0f;
    }
    if (raw_val < calib->raw_zero) {
        float norm = (float)(raw_val - calib->raw_zero) * calib->scale_neg;
        return (norm < -1.0f) ? -1.0f : norm;
    } else {
        float norm = (float)(raw_val - calib->raw_zero) * calib->scale_pos;
        return (norm > 1.0f) ? 1.0f : norm;
    }
}
