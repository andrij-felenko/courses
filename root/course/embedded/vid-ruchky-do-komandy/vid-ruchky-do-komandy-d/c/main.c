#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Параметри калібрування та мертвої зони для однієї осі */
typedef struct {
    float raw_min;         /* Мінімальний відлік АЦП (наприклад, 1000.0f) */
    float raw_center;      /* Відлік спокою в центрі (наприклад, 1500.0f) */
    float raw_max;         /* Максимальний відлік АЦП (наприклад, 2000.0f) */
    float deadband_center; /* Мертва зона центру [0.0 .. 0.15], наприклад 0.04f */
    float deadband_end;    /* Мертва зона упору [0.0 .. 0.10], наприклад 0.02f */
} stick_geometry_t;

/* Налаштування моделі швидкостей Actual Rates */
typedef struct {
    float center_rate;     /* Чутливість біля нуля (deg/s), наприклад 200.0f */
    float max_rate;        /* Максимальна швидкість (deg/s), наприклад 850.0f */
    float expo;            /* Експонента [0.0 .. 1.0], наприклад 0.55f */
} stick_rates_t;

/* Стан фільтра згладжування PT1 */
typedef struct {
    float state;           /* Поточний згладжений вихід */
    float cutoff_hz;       /* Частота зрізу (Гц), наприклад 45.0f */
} stick_filter_t;

/* Обробка одного відліку осі: повертає цільову кутову швидкість у deg/s */
float process_stick_axis(const stick_geometry_t *geom,
                         const stick_rates_t *rates,
                         stick_filter_t *filt,
                         float raw_input,
                         float dt_sec)
{
    /* 1. Триточкова нормалізація в діапазон [-1.0 .. +1.0] */
    float norm = 0.0f;
    if (raw_input >= geom->raw_center) {
        float span = geom->raw_max - geom->raw_center;
        norm = (span > 1e-3f) ? (raw_input - geom->raw_center) / span : 0.0f;
    } else {
        float span = geom->raw_center - geom->raw_min;
        norm = (span > 1e-3f) ? (raw_input - geom->raw_center) / span : 0.0f;
    }
    if (norm > 1.0f) norm = 1.0f;
    if (norm < -1.0f) norm = -1.0f;

    /* 2. Плавне ремасштабування мертвої зони без розривів */
    float sign = (norm >= 0.0f) ? 1.0f : -1.0f;
    float abs_x = fabsf(norm);
    float active_x = 0.0f;

    if (abs_x > geom->deadband_center) {
        if (abs_x >= (1.0f - geom->deadband_end)) {
            active_x = 1.0f;
        } else {
            float range = 1.0f - geom->deadband_center - geom->deadband_end;
            active_x = (range > 1e-3f) ? (abs_x - geom->deadband_center) / range : 0.0f;
        }
    }
    float stick_pos = sign * active_x;

    /* 3. Модель Actual Rates з кубічно-степеневою експонентою */
    float x = fabsf(stick_pos);
    float x5 = x * x * x * x * x;
    float curve = x * (1.0f - rates->expo) + x5 * rates->expo;
    float raw_rate = sign * (x * rates->center_rate + (rates->max_rate - rates->center_rate) * curve);

    /* 4. Низькочастотна фільтрація PT1 */
    if (dt_sec > 0.0f && filt->cutoff_hz > 0.0f) {
        float rc = 1.0f / (2.0f * 3.14159265f * filt->cutoff_hz);
        float alpha = dt_sec / (rc + dt_sec);
        if (alpha > 1.0f) alpha = 1.0f;
        filt->state += alpha * (raw_rate - filt->state);
    } else {
        filt->state = raw_rate;
    }

    return filt->state;
}
