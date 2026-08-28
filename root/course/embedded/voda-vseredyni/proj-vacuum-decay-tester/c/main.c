#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX_SAMPLES 128

typedef enum {
    TEST_STATE_IDLE = 0,
    TEST_STATE_EVACUATION,
    TEST_STATE_SETTLING,
    TEST_STATE_MEASURING,
    TEST_STATE_PASSED,
    TEST_STATE_FAILED_LEAK,
    TEST_STATE_FAILED_TIMEOUT
} vacuum_test_state_t;

typedef struct {
    float target_vacuum_kpa;     /* Цільове розрідження (наприклад, 30.0 кПа) */
    float max_leak_rate_kpa_min;  /* Граничний витік (наприклад, 0.10 кПа/хв) */
    uint32_t settling_time_ms;    /* Час стабілізації (наприклад, 15000 мс) */
    uint32_t measure_time_ms;     /* Час вимірювання (наприклад, 45000 мс) */
} vacuum_config_t;

typedef struct {
    vacuum_config_t config;
    vacuum_test_state_t state;
    uint32_t state_start_ms;
    float start_pressure_kpa;
    float current_pressure_kpa;
    float calculated_leak_rate_kpa_min;

    /* Буфер регресії OLS */
    float time_sec[MAX_SAMPLES];
    float pressure_kpa[MAX_SAMPLES];
    size_t sample_count;
    uint32_t last_sample_ms;
} vacuum_tester_t;

void vacuum_tester_init(vacuum_tester_t *t, const vacuum_config_t *cfg) {
    if (!t || !cfg) return;
    t->config = *cfg;
    t->state = TEST_STATE_IDLE;
    t->calculated_leak_rate_kpa_min = 0.0f;
    t->sample_count = 0;
}

void vacuum_tester_start(vacuum_tester_t *t, float ambient_pressure_kpa, uint32_t now_ms) {
    if (!t) return;
    t->start_pressure_kpa = ambient_pressure_kpa;
    t->current_pressure_kpa = ambient_pressure_kpa;
    t->state = TEST_STATE_EVACUATION;
    t->state_start_ms = now_ms;
    t->sample_count = 0;
    t->last_sample_ms = now_ms;
}

static float compute_linear_slope_ols(const float *x, const float *y, size_t n) {
    if (n < 2) return 0.0f;
    float sum_x = 0.0f, sum_y = 0.0f, sum_xy = 0.0f, sum_xx = 0.0f;
    for (size_t i = 0; i < n; ++i) {
        sum_x += x[i];
        sum_y += y[i];
        sum_xy += x[i] * y[i];
        sum_xx += x[i] * x[i];
    }
    float denom = (float)n * sum_xx - sum_x * sum_x;
    if (denom == 0.0f) return 0.0f;
    return ((float)n * sum_xy - sum_x * sum_y) / denom;
}

void vacuum_tester_update(vacuum_tester_t *t, float p_kpa, uint32_t now_ms, bool *pump_en, bool *valv_en) {
    if (!t) return;
    t->current_pressure_kpa = p_kpa;
    uint32_t elapsed = now_ms - t->state_start_ms;

    switch (t->state) {
        case TEST_STATE_EVACUATION:
            if (pump_en) *pump_en = true;
            if (valv_en) *valv_en = true;
            /* Перевіряємо досягнення розрідження */
            if ((t->start_pressure_kpa - p_kpa) >= t->config.target_vacuum_kpa) {
                t->state = TEST_STATE_SETTLING;
                t->state_start_ms = now_ms;
                if (pump_en) *pump_en = false;
            } else if (elapsed > 30000) { /* Таймаут відкачування 30 с */
                t->state = TEST_STATE_FAILED_TIMEOUT;
                if (pump_en) *pump_en = false;
                if (valv_en) *valv_en = false;
            }
            break;

        case TEST_STATE_SETTLING:
            if (pump_en) *pump_en = false;
            if (valv_en) *valv_en = true;
            if (elapsed >= t->config.settling_time_ms) {
                t->state = TEST_STATE_MEASURING;
                t->state_start_ms = now_ms;
                t->sample_count = 0;
                t->last_sample_ms = now_ms;
            }
            break;

        case TEST_STATE_MEASURING:
            if (pump_en) *pump_en = false;
            if (valv_en) *valv_en = true;

            /* Вибірка раз на 500 мс */
            if (now_ms - t->last_sample_ms >= 500 && t->sample_count < MAX_SAMPLES) {
                t->time_sec[t->sample_count] = (float)elapsed / 1000.0f;
                t->pressure_kpa[t->sample_count] = p_kpa;
                t->sample_count++;
                t->last_sample_ms = now_ms;
            }

            if (elapsed >= t->config.measure_time_ms) {
                float slope_kpa_per_sec = compute_linear_slope_ols(t->time_sec, t->pressure_kpa, t->sample_count);
                /* Переводимо в кПа/хв */
                t->calculated_leak_rate_kpa_min = slope_kpa_per_sec * 60.0f;

                if (t->calculated_leak_rate_kpa_min <= t->config.max_leak_rate_kpa_min) {
                    t->state = TEST_STATE_PASSED;
                } else {
                    t->state = TEST_STATE_FAILED_LEAK;
                }
                if (valv_en) *valv_en = false;
            }
            break;

        default:
            if (pump_en) *pump_en = false;
            if (valv_en) *valv_en = false;
            break;
    }
}
