/* jeita_guard.h / jeita_guard.c — Програмний сторож температурного профілю */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    JEITA_ZONE_COLD = 0,    /* T < 0 °C: Заряд суворо заборонено (0 мА) */
    JEITA_ZONE_COOL,        /* 0..10 °C: Знижений струм (0.2C..0.5C), 4.20 В */
    JEITA_ZONE_STANDARD,    /* 10..45 °C: Повний номінальний струм (1.0C), 4.20 В */
    JEITA_ZONE_WARM,        /* 45..60 °C: Помірний струм (0.5C), знижена напруга (4.10 В) */
    JEITA_ZONE_HOT          /* T >= 60 °C: Заряд суворо заборонено (0 мА) */
} jeita_zone_t;

typedef struct {
    float temp_c;           /* Поточна згладжена температура, °C */
    float temp_rate;        /* Швидкість зміни dT/dt, °C/с */
    jeita_zone_t zone;      /* Поточна активна зона */
    uint16_t charge_i_ma;   /* Дозволений струм заряду, мА */
    uint16_t charge_v_mv;   /* Гранична напруга заряду, мВ */
    bool charge_enable;     /* Дозвіл роботи силового каскаду */
    bool fault_latch;       /* Аварійне апаратне блокування */
} jeita_status_t;

typedef struct {
    float t_cold;           /* Поріг холоду: 0.0 °C */
    float t_cool;           /* Поріг прохолоди: 10.0 °C */
    float t_warm;           /* Поріг тепла: 45.0 °C */
    float t_hot;            /* Поріг спеки: 60.0 °C */
    float t_hyst;           /* Гістерезис переходів: 2.0 °C */
    float max_dt_rate;      /* Гранична швидкість нагріву: 1.5 °C/с */
    uint16_t i_standard_ma; /* Номінальний струм CC: наприклад, 2000 мА */
    uint16_t i_reduced_ma;  /* Знижений струм: наприклад, 500 мА */
    uint16_t v_standard_mv; /* Номінальна напруга CV: 4200 мВ */
    uint16_t v_reduced_mv;  /* Знижена напруга CV: 4100 мВ */
} jeita_config_t;

/* Розрахунок температури NTC за формулою бета-коефіцієнта */
float ntc_calc_temperature_c(uint16_t adc_raw, uint16_t adc_max, float r_pullup, float r_ntc_25, float beta) {
    if (adc_raw == 0 || adc_raw >= adc_max) {
        return (adc_raw == 0) ? -50.0f : 120.0f; /* Обрив або коротке датчика */
    }
    float v_ratio = (float)adc_raw / (float)adc_max;
    float r_ntc = r_pullup * (v_ratio / (1.0f - v_ratio));
    
    /* T = 1 / ( (1/T0) + (1/B)*ln(R/R0) ) */
    const float t0_kelvin = 298.15f; /* 25 °C */
    float inv_t = (1.0f / t0_kelvin) + (1.0f / beta) * logf(r_ntc / r_ntc_25);
    return (1.0f / inv_t) - 273.15f;
}

/* Оновлення стану профілю з урахуванням гістерезису та швидкості зростання температури */
void jeita_guard_update(jeita_status_t *stat, const jeita_config_t *cfg, float measured_temp, float dt_sec) {
    if (stat->fault_latch) {
        stat->charge_enable = false;
        stat->charge_i_ma = 0;
        return;
    }

    if (dt_sec > 0.001f) {
        stat->temp_rate = (measured_temp - stat->temp_c) / dt_sec;
    }
    stat->temp_c = measured_temp;

    /* Перевірка на аномальний градієнт саморозігріву */
    if (stat->temp_rate > cfg->max_dt_rate && stat->temp_c > cfg->t_cool) {
        stat->fault_latch = true;
        stat->charge_enable = false;
        stat->charge_i_ma = 0;
        return;
    }

    /* Автомат переходу між зонами з гістерезисом cfg->t_hyst */
    switch (stat->zone) {
        case JEITA_ZONE_COLD:
            if (stat->temp_c >= (cfg->t_cold + cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_COOL;
            }
            break;
        case JEITA_ZONE_COOL:
            if (stat->temp_c < cfg->t_cold) {
                stat->zone = JEITA_ZONE_COLD;
            } else if (stat->temp_c >= (cfg->t_cool + cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_STANDARD;
            }
            break;
        case JEITA_ZONE_STANDARD:
            if (stat->temp_c < (cfg->t_cool - cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_COOL;
            } else if (stat->temp_c >= cfg->t_warm) {
                stat->zone = JEITA_ZONE_WARM;
            }
            break;
        case JEITA_ZONE_WARM:
            if (stat->temp_c < (cfg->t_warm - cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_STANDARD;
            } else if (stat->temp_c >= cfg->t_hot) {
                stat->zone = JEITA_ZONE_HOT;
            }
            break;
        case JEITA_ZONE_HOT:
            if (stat->temp_c < (cfg->t_hot - cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_WARM;
            }
            break;
    }

    /* Призначення апаратних лімітів відповідно до активної зони */
    switch (stat->zone) {
        case JEITA_ZONE_COLD:
        case JEITA_ZONE_HOT:
            stat->charge_enable = false;
            stat->charge_i_ma = 0;
            stat->charge_v_mv = cfg->v_standard_mv;
            break;
        case JEITA_ZONE_COOL:
            stat->charge_enable = true;
            stat->charge_i_ma = cfg->i_reduced_ma;
            stat->charge_v_mv = cfg->v_standard_mv;
            break;
        case JEITA_ZONE_STANDARD:
            stat->charge_enable = true;
            stat->charge_i_ma = cfg->i_standard_ma;
            stat->charge_v_mv = cfg->v_standard_mv;
            break;
        case JEITA_ZONE_WARM:
            stat->charge_enable = true;
            stat->charge_i_ma = cfg->i_reduced_ma;
            stat->charge_v_mv = cfg->v_reduced_mv;
            break;
    }
}
