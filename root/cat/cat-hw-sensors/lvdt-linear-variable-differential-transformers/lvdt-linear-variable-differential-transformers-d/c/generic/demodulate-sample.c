#include <math.h>
#include <stdint.h>

typedef struct {
    float inphase_accum;
    float quadrature_accum;
    uint32_t sample_count;
} DemodulatorState;

void demodulate_sample(DemodulatorState *state, float adc_sample, float phase_angle_rad) {
    // Множення вибірки ADC на опорні синусоїду та косинусоїду
    float ref_inphase = cosf(phase_angle_rad);
    float ref_quadrature = sinf(phase_angle_rad);
    
    state->inphase_accum += adc_sample * ref_inphase;
    state->quadrature_accum += adc_sample * ref_quadrature;
    state->sample_count++;
}

float calculate_signed_displacement(const DemodulatorState *state, float scale_factor) {
    if (state->sample_count == 0) return 0.0f;
    // Обчислення середнього значення синфазної складової (ігноруючи квадратуру)
    float mean_inphase = state->inphase_accum / (float)state->sample_count;
    return mean_inphase * scale_factor;
}
