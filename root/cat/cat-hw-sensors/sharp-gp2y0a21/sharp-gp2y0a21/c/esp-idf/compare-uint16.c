#include <stdint.h>
#include <stdlib.h>

static int compare_uint16(const void *a, const void *b) {
    return (*(uint16_t *)a - *(uint16_t *)b);
}

uint16_t filter_median_5(uint16_t *samples) {
    uint16_t buf[5];
    for (int i = 0; i < 5; i++) buf[i] = samples[i];
    qsort(buf, 5, sizeof(uint16_t), compare_uint16);
    return buf[2];
}

float calculate_distance_cm(uint16_t adc_raw) {
    const float coeff_a = 4800.0f;
    const float coeff_b = 20.0f;
    if (adc_raw <= coeff_b) return 80.0f;
    float dist = coeff_a / ((float)adc_raw - coeff_b);
    if (dist > 80.0f) return 80.0f;
    if (dist < 10.0f) return 10.0f;
    return dist;
}
