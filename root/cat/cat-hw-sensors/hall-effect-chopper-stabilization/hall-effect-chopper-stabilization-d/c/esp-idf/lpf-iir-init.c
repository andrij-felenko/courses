#include <stdint.h>
#include <math.h>

typedef struct {
    float alpha;
    float prev_output;
} lpf_iir_t;

void lpf_iir_init(lpf_iir_t *filter, float cutoff_hz, float sample_rate_hz) {
    float dt = 1.0f / sample_rate_hz;
    float omega = 2.0f * 3.14159265f * cutoff_hz;
    filter->alpha = (omega * dt) / (1.0f + omega * dt);
    filter->prev_output = 0.0f;
}

float lpf_iir_process(lpf_iir_t *filter, float raw_adc_volts) {
    float filtered = filter->alpha * raw_adc_volts + (1.0f - filter->alpha) * filter->prev_output;
    filter->prev_output = filtered;
    return filtered;
}
