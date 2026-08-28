/* tia_processor.h / tia_processor.c — Модуль обробки фотоструму TIA */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    float feedback_resistor_ohms; /* Опір Rf (наприклад, 1.0e6f = 1 МОм) */
    float dark_current_t0_amps;   /* Базовий темновий струм за температури T0 */
    float cal_temp_celsius;       /* Температура T0 (°C) */
    float temp_doubling_step_c;   /* Крок подвоєння Id (типово 8.5 °C) */
    float filter_alpha;           /* Коефіцієнт IIR-фільтрації (0.01..1.0) */
    float adc_vref_volts;         /* Опорна напруга АЦП (В) */
    float sat_margin_volts;       /* Запас до шини насичення (В) */
} TiaConfig;

typedef struct {
    float filtered_voltage;
    float last_dark_voltage;
    float last_temperature_c;
} TiaState;

typedef struct {
    float photocurrent_amps;      /* Обчислений чистий фотострум (А) */
    float output_voltage_volts;   /* Відфільтрована напруга корисного сигналу (В) */
    float estimated_dark_amps;    /* Теоретичний темновий струм за поточної T */
    bool is_saturated;            /* Прапорець перевантаження аналогового тракту */
    bool is_valid;                /* Прапорець достовірності даних */
} TiaMeasurement;

void tia_init(TiaState *state, const TiaConfig *cfg) {
    state->filtered_voltage = 0.0f;
    state->last_dark_voltage = 0.0f;
    state->last_temperature_c = cfg->cal_temp_celsius;
}

/* Оцінка темнового струму за експоненційною моделлю */
float tia_calc_dark_current(const TiaConfig *cfg, float temp_celsius) {
    float delta_t = temp_celsius - cfg->cal_temp_celsius;
    float exponent = delta_t / cfg->temp_doubling_step_c;
    return cfg->dark_current_t0_amps * powf(2.0f, exponent);
}

/* Обробка циклу подвійної корельованої вибірки */
TiaMeasurement tia_process_sample(TiaState *state,
                                  const TiaConfig *cfg,
                                  float raw_dark_adc_v,
                                  float raw_light_adc_v,
                                  float current_temp_c) {
    TiaMeasurement result;
    
    state->last_dark_voltage = raw_dark_adc_v;
    state->last_temperature_c = current_temp_c;
    
    /* Перевірка на насичення аналогового каскаду */
    float max_linear_v = cfg->adc_vref_volts - cfg->sat_margin_volts;
    if (raw_light_adc_v >= max_linear_v || raw_light_adc_v <= cfg->sat_margin_volts) {
        result.is_saturated = true;
        result.is_valid = false;
    } else {
        result.is_saturated = false;
        result.is_valid = true;
    }

    /* CDS-віднімання базової лінії темряви */
    float diff_v = raw_light_adc_v - raw_dark_adc_v;
    if (diff_v < 0.0f) {
        diff_v = 0.0f; /* Відсікання негативного шуму */
    }

    /* Експоненційне згладжування (IIR-фільтр першого порядку) */
    state->filtered_voltage = (cfg->filter_alpha * diff_v) +
                              ((1.0f - cfg->filter_alpha) * state->filtered_voltage);

    result.output_voltage_volts = state->filtered_voltage;
    result.photocurrent_amps = state->filtered_voltage / cfg->feedback_resistor_ohms;
    result.estimated_dark_amps = tia_calc_dark_current(cfg, current_temp_c);

    return result;
}
