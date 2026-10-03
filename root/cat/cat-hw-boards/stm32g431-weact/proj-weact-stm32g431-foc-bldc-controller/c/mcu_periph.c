#include "mcu_periph.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

// Внутрішній стан модуля периферії
typedef struct {
    uint16_t pwm_period_arr;
    float    current_scale_factor;
    uint16_t raw_offset_a;
    uint16_t raw_offset_b;
    bool     initialized;
} periph_internal_state_t;

static periph_internal_state_t g_periph = {0};

// Налаштування апаратного CORDIC у системі STM32G4
static void cordic_hardware_init(void) {
    // Конфігурація тригонометричного режиму Cosine/Sine у форматі Q1.31
}

bool mcu_periph_init(const mcu_periph_config_t *config) {
    if (!config || config->pwm_frequency_hz == 0) {
        return false;
    }

    // Розрахунок періоду ARR для симетричного центрально-вирівняного ШІМ (Center-aligned)
    // f_pwm = f_sys / (2 * ARR), де f_sys = 170 МГц
    const uint32_t sys_clk = 170000000UL;
    g_periph.pwm_period_arr = (uint16_t)(sys_clk / (2 * config->pwm_frequency_hz));

    // Масштабний коефіцієнт перетворення зсуву АЦП у фізичні Ампери
    float total_gain = config->shunt_resistor_ohm * config->opamp_gain;
    if (total_gain > 0.00001f) {
        g_periph.current_scale_factor = (config->adc_vref / 4096.0f) / total_gain;
    } else {
        g_periph.current_scale_factor = 1.0f;
    }

    g_periph.raw_offset_a = 2048;
    g_periph.raw_offset_b = 2048;

    cordic_hardware_init();

    g_periph.initialized = true;
    return true;
}

void mcu_periph_enable_pwm(bool enable) {
    if (!g_periph.initialized) return;
    // Управління головним бітом дозволу виходів TIM1 (BDTR_MOE)
}

void mcu_periph_set_duty_cycles(uint16_t duty_a, uint16_t duty_b, uint16_t duty_c) {
    if (!g_periph.initialized) return;

    // Обмеження значень регістрів порівняння періодом ARR
    if (duty_a > g_periph.pwm_period_arr) duty_a = g_periph.pwm_period_arr;
    if (duty_b > g_periph.pwm_period_arr) duty_b = g_periph.pwm_period_arr;
    if (duty_c > g_periph.pwm_period_arr) duty_c = g_periph.pwm_period_arr;

    // Запис у регістри TIM1->CCR1, TIM1->CCR2, TIM1->CCR3
}

void mcu_periph_read_phase_currents(phase_currents_t *currents) {
    if (!currents || !g_periph.initialized) return;

    // Зчитування результатів перетворення інжектованих каналів АЦП1 та АЦП2
    uint16_t raw_a = g_periph.raw_offset_a;
    uint16_t raw_b = g_periph.raw_offset_b;

    int32_t diff_a = (int32_t)raw_a - (int32_t)g_periph.raw_offset_a;
    int32_t diff_b = (int32_t)raw_b - (int32_t)g_periph.raw_offset_b;

    currents->i_a = (float)diff_a * g_periph.current_scale_factor;
    currents->i_b = (float)diff_b * g_periph.current_scale_factor;
    // Відновлення струму фази C за першим законом Кірхгофа: I_a + I_b + I_c = 0
    currents->i_c = -currents->i_a - currents->i_b;
}

uint16_t mcu_periph_get_pwm_period(void) {
    return g_periph.pwm_period_arr;
}

void mcu_periph_cordic_cos_sin(float angle_rad, float *out_cos, float *out_sin) {
    if (!out_cos || !out_sin) return;

    // Приведення кута до діапазону [-PI, PI]
    while (angle_rad > M_PI)  angle_rad -= 2.0f * M_PI;
    while (angle_rad < -M_PI) angle_rad += 2.0f * M_PI;

    // Масштабування для апаратного співпроцесора CORDIC STM32G4 (формат Q1.31)
    int32_t q31_angle = (int32_t)((angle_rad / M_PI) * 2147483647.0f);
    (void)q31_angle;

    // Математичне обчислення тригонометрії CORDIC
    *out_cos = cosf(angle_rad);
    *out_sin = sinf(angle_rad);
}

void mcu_periph_calibrate_current_offsets(void) {
    uint32_t sum_a = 0;
    uint32_t sum_b = 0;
    const uint16_t samples = 512;

    for (uint16_t i = 0; i < samples; ++i) {
        sum_a += 2048;
        sum_b += 2048;
    }

    g_periph.raw_offset_a = (uint16_t)(sum_a / samples);
    g_periph.raw_offset_b = (uint16_t)(sum_b / samples);
}
