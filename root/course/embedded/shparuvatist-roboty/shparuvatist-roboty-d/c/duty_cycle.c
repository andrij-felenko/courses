#include "duty_cycle.h"

#include <math.h>
#include <stddef.h>

/* 24 год · 365.25 доби — рік з урахуванням високосних. */
#define HOURS_PER_YEAR 8766.0

const char *duty_strerror(duty_status st)
{
    switch (st) {
    case DUTY_OK:              return "гаразд";
    case DUTY_ERR_ARGS:        return "порожній вказівник в аргументах";
    case DUTY_ERR_PERIOD:      return "період циклу мусить бути додатним";
    case DUTY_ERR_WINDOW:      return "активне вікно порожнє або довше за період";
    case DUTY_ERR_CURRENT:     return "очікуємо 0 <= I_sleep < I_on";
    case DUTY_ERR_BATTERY:     return "ємність або коефіцієнт віддачі поза межами";
    case DUTY_ERR_TARGET:      return "цільовий термін служби мусить бути додатним";
    case DUTY_ERR_UNREACHABLE: return "мети не досягти: сам струм спокою вичерпає джерело";
    }
    return "невідомий код помилки";
}

/* Перевірки навмисно записані через заперечення (!(x > 0) замість x <= 0):
 * NaN, що приходить із недовиміряного лога споживання, теж провалює
 * перевірку, а не прослизає далі й не отруює всі похідні числа. */
static duty_status duty_validate(const duty_config *cfg)
{
    if (cfg == NULL)
        return DUTY_ERR_ARGS;
    if (!(cfg->period_s > 0.0))
        return DUTY_ERR_PERIOD;
    if (!(cfg->t_on_s > 0.0) || cfg->t_on_s > cfg->period_s)
        return DUTY_ERR_WINDOW;
    if (!(cfg->i_sleep_ua >= 0.0) || !(cfg->i_on_ua > cfg->i_sleep_ua))
        return DUTY_ERR_CURRENT;
    if (!(cfg->capacity_mah > 0.0) || !(cfg->derating > 0.0) || cfg->derating > 1.0)
        return DUTY_ERR_BATTERY;
    return DUTY_OK;
}

/* Ефективна ємність у мкА·год: номінал за відрахуванням саморозряду,
 * просідання на внутрішньому опорі й морозу. */
static double duty_effective_capacity_uah(const duty_config *cfg)
{
    return cfg->capacity_mah * cfg->derating * 1000.0;
}

duty_status duty_evaluate(const duty_config *cfg, duty_result *out)
{
    duty_status st;
    duty_result r = {0};
    double t_off_s, q_total, ratio;

    if (out == NULL)
        return DUTY_ERR_ARGS;
    st = duty_validate(cfg);
    if (st != DUTY_OK)
        return st;

    t_off_s = cfg->period_s - cfg->t_on_s;

    r.duty = cfg->t_on_s / cfg->period_s;
    r.q_on_uas = cfg->i_on_ua * cfg->t_on_s;
    r.q_off_uas = cfg->i_sleep_ua * t_off_s;

    /* I_avg = (I_on·t_on + I_sleep·t_off) / T — зважена сума, а не струм радіо. */
    q_total = r.q_on_uas + r.q_off_uas;
    r.i_avg_ua = q_total / cfg->period_s;
    r.active_share_pct = 100.0 * r.q_on_uas / q_total;
    r.sleep_share_pct = 100.0 * r.q_off_uas / q_total;
    r.k_energy = r.q_off_uas / r.q_on_uas; /* q_on > 0 гарантує перевірка вікна */

    r.lifetime_h = duty_effective_capacity_uah(cfg) / r.i_avg_ua;
    r.lifetime_years = r.lifetime_h / HOURS_PER_YEAR;

    /* Точки, де сон зрівнюється з активним спалахом (k = 1) і давить його
     * дев'ятикратно (k = 9). Розв'язок рівняння I_sleep·(T − t_on) = k·I_on·t_on
     * точний; формула статті T = k·(I_on/I_sleep)·t_on нехтує одним доданком
     * t_on, і при D << 1 різниця між ними — соті частки відсотка. */
    if (cfg->i_sleep_ua > 0.0) {
        ratio = cfg->i_on_ua / cfg->i_sleep_ua;
        r.t_eq_s = cfg->t_on_s * (1.0 + ratio);
        r.t_sat_s = cfg->t_on_s * (1.0 + 9.0 * ratio);
    } else {
        /* Ідеального нуля струму спокою не буває, але модель мусить його
         * пережити: без витоків сон ніколи не переважить спалах. */
        r.t_eq_s = INFINITY;
        r.t_sat_s = INFINITY;
    }

    *out = r;
    return DUTY_OK;
}

duty_status duty_min_period(const duty_config *cfg, double target_years, double *period_s)
{
    duty_status st;
    double i_avg_max;

    if (period_s == NULL)
        return DUTY_ERR_ARGS;
    st = duty_validate(cfg);
    if (st != DUTY_OK)
        return st;
    if (!(target_years > 0.0))
        return DUTY_ERR_TARGET;

    /* Стеля середнього струму, за якої джерела ще стачає на цільовий термін. */
    i_avg_max = duty_effective_capacity_uah(cfg) / (target_years * HOURS_PER_YEAR);

    /* Асимптота закону: I_avg прямує до I_sleep, а не до нуля. Якщо стеля
     * нижча за струм спокою, розтягування періоду не рятує взагалі. */
    if (i_avg_max <= cfg->i_sleep_ua)
        return DUTY_ERR_UNREACHABLE;

    /* Бюджету стачає навіть на безперервну роботу — сон не потрібен. */
    if (i_avg_max >= cfg->i_on_ua) {
        *period_s = cfg->t_on_s;
        return DUTY_OK;
    }

    /* T_min = (I_on − I_sleep)·t_on / (I_avg_max − I_sleep) */
    *period_s = (cfg->i_on_ua - cfg->i_sleep_ua) * cfg->t_on_s
                / (i_avg_max - cfg->i_sleep_ua);
    return DUTY_OK;
}

const etsi_band ETSI_EU868[ETSI_EU868_COUNT] = {
    { "g1", 868.00, 868.60, 0.010, 14.0 }, /* основний LoRaWAN, 36 с/год */
    { "g2", 868.70, 869.20, 0.001, 14.0 }, /* 3.6 с/год */
    { "g3", 869.40, 869.65, 0.100, 27.0 }  /* шлюзи, 6 хв/год */
};

const etsi_band *etsi_band_for(double freq_mhz)
{
    int i;

    for (i = 0; i < ETSI_EU868_COUNT; ++i) {
        if (freq_mhz >= ETSI_EU868[i].f_lo_mhz && freq_mhz <= ETSI_EU868[i].f_hi_mhz)
            return &ETSI_EU868[i];
    }
    return NULL; /* частота поза сіткою EU868 — судити нема за чим */
}

duty_status duty_check_airtime(const etsi_band *band, double toa_s,
                               double period_s, airtime_check *out)
{
    double sessions_per_hour;

    if (band == NULL || out == NULL)
        return DUTY_ERR_ARGS;
    if (!(toa_s > 0.0))
        return DUTY_ERR_WINDOW;
    if (!(period_s > 0.0))
        return DUTY_ERR_PERIOD;

    sessions_per_hour = 3600.0 / period_s;

    out->allowance_s = 3600.0 * band->duty_limit;
    out->used_s = toa_s * sessions_per_hour;
    out->used_pct = 100.0 * out->used_s / out->allowance_s;
    out->packet_share_pct = 100.0 * toa_s / out->allowance_s;
    out->packets_per_hour = out->allowance_s / toa_s;
    /* Мінімальний період між пакетами: t_air / D_limit. */
    out->min_period_s = toa_s / band->duty_limit;
    out->compliant = (out->used_s <= out->allowance_s);

    return DUTY_OK;
}
