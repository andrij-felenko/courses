#include <stdint.h>

#define SAMPLES_COUNT 5

uint8_t decode_rotary_position(const uint16_t adc_samples[SAMPLES_COUNT], const uint16_t thresholds[16]) {
    uint16_t sorted[SAMPLES_COUNT];
    for (uint8_t i = 0; i < SAMPLES_COUNT; i++) {
        sorted[i] = adc_samples[i];
    }
    for (uint8_t i = 0; i < SAMPLES_COUNT - 1; i++) {
        for (uint8_t j = i + 1; j < SAMPLES_COUNT; j++) {
            if (sorted[i] > sorted[j]) {
                uint16_t temp = sorted[i];
                sorted[i] = sorted[j];
                sorted[j] = temp;
            }
        }
    }
    uint16_t v_sample = sorted[2];

    uint8_t low = 0;
    uint8_t high = 15;
    while (low < high) {
        uint8_t mid = low + (high - low) / 2;
        if (v_sample <= thresholds[mid]) {
            high = mid;
        } else {
            low = mid + 1;
        }
    }
    return low;
}
