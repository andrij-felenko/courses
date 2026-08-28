/* tia_filter.h / tia_filter.c — Драйвер оптичного фронтенду */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    float rf_ohms;              /* Опір зворотного зв'язку Rf (Ом) */
    float base_dark_current_a;  /* Базовий темновий струм Id0 за T0 (А) */
    float t0_celsius;           /* Базова температура калібрування T0 (°C) */
    float temp_doubling_step_c; /* Крок подвоєння струму (типово 8.5 °C) */
    float ema_alpha;            /* Коефіцієнт згладжування фільтра (0.01..1.0) */
    float v_adc_ref_v;          /* Опорна напруга АЦП (В) */
    float v_sat_margin_v;       /* Запас до межі живлення ОП (В) */
} TiaFilterConfig;

typedef struct {
    float filtered_output_v;
    float last_raw_dark_v;
    float last_raw_light_v;
} TiaFilterState;

typedef struct {
    float photocurrent_a;       /* Чистий виміряний фотострум (А) */
    float clean_voltage_v;      /* Очищена вихідна напруга сигналу (В) */
    float estimated_dark_a;     /* Оцінений темновий струм за поточної T (А) */
    bool is_saturated;          /* Прапорець насичення підсилювача */
    bool is_valid;              /* Прапорець валідності вимірювання */
} TiaFilterResult;

void tia_filter_init(TiaFilterState *state, const TiaFilterConfig *cfg) {
    state->filtered_output_v = 0.0f;
    state->last_raw_dark_v = 0.0f;
    state->last_raw_light_v = 0.0f;
}

/* Аналітичний розрахунок очікуваного темнового струму */
float tia_filter_calc_dark(const TiaFilterConfig *cfg, float temp_c) {
    float delta_t = temp_c - cfg->t0_celsius;
    float exponent = delta_t / cfg->temp_doubling_step_c;
    return cfg->base_dark_current_a * powf(2.0f, exponent);
}

/* Обробка циклу подвійної корельованої вибірки (CDS) */
TiaFilterResult tia_filter_process_cds(TiaFilterState *state,
                                       const TiaFilterConfig *cfg,
                                       float raw_dark_v,
                                       float raw_light_v,
                                       float current_temp_c) {
    TiaFilterResult res;
    state->last_raw_dark_v = raw_dark_v;
    state->last_raw_light_v = raw_light_v;

    /* Перевірка на перевантаження / вихід за лінійний діапазон */
    float max_linear_v = cfg->v_adc_ref_v - cfg->v_sat_margin_v;
    if (raw_light_v >= max_linear_v || raw_light_v <= cfg->v_sat_margin_v) {
        res.is_saturated = true;
        res.is_valid = false;
    } else {
        res.is_saturated = false;
        res.is_valid = true;
    }

    /* Віднімання темнового зміщення (CDS) */
    float delta_v = raw_light_v - raw_dark_v;
    if (delta_v < 0.0f) {
        delta_v = 0.0f; /* Відсікання від'ємних шумових сплесків */
    }

    /* Експоненційне згладжування (IIR-фільтр низьких частот) */
    state->filtered_output_v = (cfg->ema_alpha * delta_v) +
                               ((1.0f - cfg->ema_alpha) * state->filtered_output_v);

    res.clean_voltage_v = state->filtered_output_v;
    res.photocurrent_a = state->filtered_output_v / cfg->rf_ohms;
    res.estimated_dark_a = tia_filter_calc_dark(cfg, current_temp_c);

    return res;
}
