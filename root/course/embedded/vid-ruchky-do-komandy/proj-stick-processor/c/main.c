#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Конфігурація калібрування та мертвої зони для однієї осі */
typedef struct {
    float raw_min;         /* мінімальний відлік АЦП (наприклад, 1000.0f) */
    float raw_center;      /* центральний відлік у стані спокою (наприклад, 1500.0f) */
    float raw_max;         /* максимальний відлік АЦП (наприклад, 2000.0f) */
    float center_deadband; /* відносна мертва зона центру [0.0 .. 0.15] (наприклад, 0.04f) */
    float end_deadband;    /* відносна мертва зона упору [0.0 .. 0.10] (наприклад, 0.02f) */
} stick_calib_config_t;

/* Налаштування моделі швидкості Actual Rates */
typedef struct {
    float center_rate;     /* чутливість біля центру (deg/s), наприклад 200.0f */
    float max_rate;        /* максимальна кутова швидкість (deg/s), наприклад 850.0f */
    float expo;            /* ступінь пом'якшення кривої [0.0 .. 1.0], наприклад 0.55f */
} actual_rates_config_t;

/* Стан фільтра згладжування RC Smoothing (PT1) */
typedef struct {
    float state;           /* накопичений стан фільтра */
    float cutoff_hz;       /* частота зрізу фільтра (Гц), наприклад 45.0f */
} rc_filter_state_t;

/* Повний об'єкт обробки осі стіка */
typedef struct {
    stick_calib_config_t calib;
    actual_rates_config_t rates;
    rc_filter_state_t filter;
} stick_axis_processor_t;

/* Ініціалізація стану процесора осі */
void stick_processor_init(stick_axis_processor_t *proc,
                          const stick_calib_config_t *calib,
                          const actual_rates_config_t *rates,
                          float cutoff_hz)
{
    if (proc != NULL) {
        if (calib != NULL) proc->calib = *calib;
        if (rates != NULL) proc->rates = *rates;
        proc->filter.state = 0.0f;
        proc->filter.cutoff_hz = (cutoff_hz > 0.0f) ? cutoff_hz : 45.0f;
    }
}

/* 1. Нормалізація вхідного сирого сигналу в діапазон [-1.0 .. +1.0] */
static float stick_normalize(const stick_calib_config_t *calib, float raw_value)
{
    float norm = 0.0f;
    if (raw_value >= calib->raw_center) {
        float span = calib->raw_max - calib->raw_center;
        if (span > 1e-3f) {
            norm = (raw_value - calib->raw_center) / span;
        }
    } else {
        float span = calib->raw_center - calib->raw_min;
        if (span > 1e-3f) {
            norm = (raw_value - calib->raw_center) / span;
        }
    }

    /* Жорстке затискання в межі [-1.0 .. +1.0] */
    if (norm > 1.0f) norm = 1.0f;
    if (norm < -1.0f) norm = -1.0f;
    return norm;
}

/* 2. Застосування мертвої зони центру та кінцевих упорів без розривів */
static float stick_apply_deadband(const stick_calib_config_t *calib, float norm_value)
{
    float sign = (norm_value >= 0.0f) ? 1.0f : -1.0f;
    float abs_val = fabsf(norm_value);

    float db_c = calib->center_deadband;
    float db_e = calib->end_deadband;

    /* Перевірка перебування всередині мертвої зони центру */
    if (abs_val <= db_c) {
        return 0.0f;
    }

    /* Досягнення кінцевого упору */
    if (abs_val >= (1.0f - db_e)) {
        return sign * 1.0f;
    }

    /* Лінійне ремасштабування робочого діапазону від 0.0 до 1.0 */
    float active_range = 1.0f - db_c - db_e;
    if (active_range < 1e-3f) {
        return 0.0f;
    }

    float rescaled = (abs_val - db_c) / active_range;
    return sign * rescaled;
}

/* 3. Розрахунок цільової кутової швидкості за моделлю Actual Rates */
static float stick_calc_actual_rate(const actual_rates_config_t *rates, float stick_pos)
{
    float sign = (stick_pos >= 0.0f) ? 1.0f : -1.0f;
    float x = fabsf(stick_pos);

    /* Степенева крива 5-го порядку: x · (1 - e) + x⁵ · e */
    float x5 = x * x * x * x * x;
    float curve = x * (1.0f - rates->expo) + x5 * rates->expo;

    /* Розрахунок кутової швидкості (deg/s) */
    float center_contrib = x * rates->center_rate;
    float max_contrib = (rates->max_rate - rates->center_rate) * curve;
    float rate_deg_s = center_contrib + max_contrib;

    return sign * rate_deg_s;
}

/* 4. Фільтр низьких частот PT1 (RC Smoothing) */
static float stick_filter_pt1(rc_filter_state_t *filt, float target_rate, float dt_seconds)
{
    if (dt_seconds <= 0.0f || filt->cutoff_hz <= 0.0f) {
        filt->state = target_rate;
        return filt->state;
    }

    /* Розрахунок коефіцієнта alpha: dt / (RC + dt) */
    float rc = 1.0f / (2.0f * 3.1415926535f * filt->cutoff_hz);
    float alpha = dt_seconds / (rc + dt_seconds);

    if (alpha > 1.0f) alpha = 1.0f;
    if (alpha < 0.0f) alpha = 0.0f;

    filt->state += alpha * (target_rate - filt->state);
    return filt->state;
}

/* Головна функція повного циклу обробки осі */
float stick_process_axis(stick_axis_processor_t *proc, float raw_input, float dt_seconds)
{
    if (proc == NULL) {
        return 0.0f;
    }

    /* Крок 1: Нормалізація */
    float norm = stick_normalize(&proc->calib, raw_input);

    /* Крок 2: Мертва зона */
    float active_stick = stick_apply_deadband(&proc->calib, norm);

    /* Крок 3: Модель швидкості Actual Rates */
    float target_rate = stick_calc_actual_rate(&proc->rates, active_stick);

    /* Крок 4: RC Smoothing */
    float smoothed_rate = stick_filter_pt1(&proc->filter, target_rate, dt_seconds);

    return smoothed_rate;
}
