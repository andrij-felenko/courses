#include <stdint.h>
#include <math.h>

// Обчислює миттєве значення струму (А) за відліком АЦП
float acs712_get_current(uint16_t adc_raw, uint16_t adc_zero, float vcc, float sensitivity, uint16_t adc_max) {
    float v_out = ((float)adc_raw / (float)adc_max) * vcc;
    float v_zero = ((float)adc_zero / (float)adc_max) * vcc;
    return (v_out - v_zero) / sensitivity;
}

// Обчислює середньоквадратичне значення (RMS) струму за N вибірок
float acs712_get_rms(const uint16_t *adc_samples, uint16_t sample_count, uint16_t adc_zero, float vcc, float sensitivity, uint16_t adc_max) {
    float sum_sq = 0.0f;
    for (uint16_t i = 0; i < sample_count; i++) {
        float i_inst = acs712_get_current(adc_samples[i], adc_zero, vcc, sensitivity, adc_max);
        sum_sq += i_inst * i_inst;
    }
    return sqrtf(sum_sq / (float)sample_count);
}
