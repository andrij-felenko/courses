#include <stdint.h>
#include <stdbool.h>

// Константи операційного циклу IronOS
#define ADC_MAX_RAW         4095.0f
#define V_REF               3.3f
#define OPAMP_GAIN          250.0f
#define SEEBECK_COEFF       0.000041f // 41 мкВ/°C для K-типу

typedef struct {
    float target_temp;
    float current_temp;
    float input_voltage;
    uint16_t pwm_duty;
    bool is_sleeping;
} IronOsState;

// Зчитування та розрахунок температури під час безнапругового інтервалу (quiet window)
float ironos_read_temperature(uint16_t adc_raw_tc, float cold_junction_temp) {
    float v_tc = ((float)adc_raw_tc / ADC_MAX_RAW) * V_REF / OPAMP_GAIN;
    float t_uncorrected = v_tc / SEEBECK_COEFF;
    return t_uncorrected + cold_junction_temp;
}

// Операційний крок ядра паяльника
void ironos_kernel_step(IronOsState *state, uint16_t adc_tc, float cold_junc, float v_in_adc) {
    // 1. Оновлення виміряної температури
    state->current_temp = ironos_read_temperature(adc_tc, cold_junc);
    
    // 2. Обчислення обмеження потужності залежно від вхідної напруги
    float p_max = (v_in_adc * v_in_adc) / 8.0f; // R_tip = 8 Ом
    float p_target = 30.0f; // Ліміт потужності 30 Вт
    float d_max = (p_max > 0.0f) ? (p_target / p_max) : 0.0f;
    if (d_max > 1.0f) d_max = 1.0f;
    
    // 3. Проста пропорційна адаптація ШІМ (спрощений приклад PID)
    float error = state->target_temp - state->current_temp;
    if (error > 0.0f) {
        float desired_duty = error * 0.05f;
        if (desired_duty > d_max) desired_duty = d_max;
        state->pwm_duty = (uint16_t)(desired_duty * 1000.0f);
    } else {
        state->pwm_duty = 0;
    }
}
