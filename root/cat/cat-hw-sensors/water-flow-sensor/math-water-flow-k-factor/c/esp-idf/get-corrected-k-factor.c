#include <stddef.h>
#include <stdbool.h>

typedef struct {
    float freq_hz;
    float k_factor;
} k_factor_point_t;

float get_corrected_k_factor(float freq_hz, const k_factor_point_t *lut, size_t lut_size) {
    if (lut_size == 0) {
        return 0.0f;
    }
    if (freq_hz <= lut[0].freq_hz) {
        return lut[0].k_factor;
    }
    if (freq_hz >= lut[lut_size - 1].freq_hz) {
        return lut[lut_size - 1].k_factor;
    }

    for (size_t i = 0; i < lut_size - 1; i++) {
        if (freq_hz >= lut[i].freq_hz && freq_hz <= lut[i + 1].freq_hz) {
            float delta_f = lut[i + 1].freq_hz - lut[i].freq_hz;
            if (delta_f <= 0.0f) {
                return lut[i].k_factor;
            }
            float weight = (freq_hz - lut[i].freq_hz) / delta_f;
            return lut[i].k_factor + weight * (lut[i + 1].k_factor - lut[i].k_factor);
        }
    }
    return lut[lut_size - 1].k_factor;
}
