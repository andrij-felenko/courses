/*
 * line_diagnostics.h - Драйвер моніторингу синфазних перешкод та цілісності лінії
 */

#ifndef LINE_DIAGNOSTICS_H
#define LINE_DIAGNOSTICS_H

#include <stdint.h>
#include <stdbool.h>

#define LINE_DIAG_SAMPLE_WINDOW_SIZE  64U

typedef enum {
    LINE_STATE_OK = 0,
    LINE_STATE_WARNING_NO_GROUND,        /* Виявлено 50 Гц витік (відсутність PE) */
    LINE_STATE_WARNING_HIGH_COMMON_MODE, /* Синфазна напруга на межі діапазону */
    LINE_STATE_CRITICAL_SURGE_EVENT,     /* Зафіксовано високовольтний сплеск */
    LINE_STATE_CRITICAL_INSULATION_FAIL  /* Пробій/деградація ізоляції < 500 кОм */
} line_safety_state_t;

typedef struct {
    float v_cm_instant_volts;   /* Миттєва синфазна напруга */
    float v_cm_dc_bias_volts;   /* Постійний зсув землі (ΔV_gnd) */
    float v_cm_noise_rms_volts; /* RMS змінного синфазного шуму */
    float insulation_res_kohm;  /* Опір ізоляції на PE */
    uint32_t surge_event_count; /* Лічильник зафіксованих перенапруг */
    line_safety_state_t state;  /* Поточний стан автомата безпеки */
} line_health_metrics_t;

typedef struct {
    /* Поріг постійної синфазної напруги для попередження (В) */
    float v_cm_warn_threshold_volts;
    /* Поріг критичного RMS шуму 50 Гц / кГц (В) */
    float v_cm_rms_warn_threshold_volts;
    /* Мінімально допустимий опір ізоляції (кОм) */
    float r_iso_min_kohm;
    /* Опорна напруга АЦП (В) */
    float adc_vref_volts;
    /* Масштабний коефіцієнт вхідного дільника (V_in / V_adc) */
    float divider_ratio;
} line_diag_config_t;

typedef struct {
    line_diag_config_t config;
    uint16_t adc_buffer[LINE_DIAG_SAMPLE_WINDOW_SIZE];
    uint32_t sample_idx;
    uint32_t surge_counter;
    line_safety_state_t current_state;
} line_diag_handle_t;

void line_diag_init(line_diag_handle_t *handle, const line_diag_config_t *config);
void line_diag_push_adc_sample(line_diag_handle_t *handle, uint16_t adc_raw);
void line_diag_process(line_diag_handle_t *handle, float raw_r_iso_adc, line_health_metrics_t *out_metrics);

#endif /* LINE_DIAGNOSTICS_H */
