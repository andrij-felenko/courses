#include "lifetime.h"

#include <math.h>

#define HOURS_PER_DAY  24.0
#define DAYS_PER_YEAR  365.25
#define PLATEAU_DEPTH  0.50   /* «робоче плато» — напруга на половині розряду */
#define ESR_BUDGET     0.50   /* половину запасу напруги віддаємо на ESR буфера */
#define HLC_THRESHOLD_F 1.0e-3 /* більше за 1000 мкФ керамікою вже не набрати */

const char *limiter_str(limiter_t l)
{
    switch (l) {
    case LIM_BROWNOUT:       return "просадка напруги нижче порогу відсічки";
    case LIM_SELF_DISCHARGE: return "саморозряд самої комірки";
    case LIM_ACTIVE_PHASE:   return "активна фаза пробудження";
    case LIM_SLEEP:          return "струм глибокого сну";
    }
    return "невідомо";
}

/* Скільки буферної ємності треба, щоб імпульс не просадив шину нижче порогу.
 * Конденсатор рахуємо так, ніби комірка під час імпульсу не дає нічого: після
 * місяця сну пасивована плівка саме так себе й поводить. */
static void size_buffer(const battery_t *b, const site_t *site,
                        const duty_result_t *duty, pulse_report_t *p)
{
    double plateau_v = battery_ocv_at(b, PLATEAU_DEPTH);
    double pulse_a = duty->peak_current_ma / 1000.0;
    double pulse_s = duty->peak_duration_ms / 1000.0;
    double usable_v;

    p->headroom_v = plateau_v - site->cutoff_v;
    p->buffer_needed = (p->brownout || p->brownout_after_storage);
    p->buffer_impossible = 0;
    p->buffer_farads = 0.0;
    p->buffer_esr_max_ohm = 0.0;

    if (!p->buffer_needed)
        return;

    if (p->headroom_v <= 0.0 || pulse_a <= 0.0) {
        /* Поріг відсічки вищий за робоче плато комірки: тут не буфер треба,
         * а інша хімія або менший поріг. */
        p->buffer_impossible = 1;
        return;
    }

    usable_v = p->headroom_v * (1.0 - ESR_BUDGET);
    p->buffer_farads = pulse_a * pulse_s / usable_v;      /* C = I·t/ΔU */
    p->buffer_esr_max_ohm = (p->headroom_v * ESR_BUDGET) / pulse_a;
}

static void analyse_pulse(const battery_t *b, const site_t *site,
                          const duty_result_t *duty, pulse_report_t *p)
{
    double pulse_ma = duty->peak_current_ma;
    double pass_factor = battery_passivation_factor(b, site->storage_days);

    p->r_int_ohm = battery_r_int(b, site->temp_c);
    p->sag_v = (pulse_ma / 1000.0) * p->r_int_ohm;        /* ΔV = I · R_int */
    p->v_term_v = b->ocv_fresh_v - p->sag_v;              /* V_term = V_ocv − ΔV */
    p->brownout = (p->v_term_v < site->cutoff_v);

    p->r_passivated_ohm = p->r_int_ohm * pass_factor;
    p->sag_storage_v = (pulse_ma / 1000.0) * p->r_passivated_ohm;
    p->v_term_storage_v = b->ocv_fresh_v - p->sag_storage_v;
    p->brownout_after_storage = (p->v_term_storage_v < site->cutoff_v);

    size_buffer(b, site, duty, p);
}

static void pick_limiter(estimate_t *e)
{
    size_t i;
    double worst = -1.0;

    if (e->pulse.brownout) {
        e->limiter = LIM_BROWNOUT;
        e->limiter_note = "передавач валить шину нижче BOD ще на свіжій комірці";
        return;
    }
    if (e->i_self_ma > e->i_avg_ma) {
        e->limiter = LIM_SELF_DISCHARGE;
        e->limiter_note = "оптимізувати прошивку далі немає сенсу";
        return;
    }
    if (e->duty.q_sleep_mas > e->duty.q_active_mas + e->duty.q_depass_mas) {
        e->limiter = LIM_SLEEP;
        e->limiter_note = "шукати паразитні витоки й струм спокою стабілізатора";
        return;
    }

    e->limiter = LIM_ACTIVE_PHASE;
    e->limiter_note = "фаза, що з'їдає найбільше заряду";
    for (i = 0; i < e->duty.count; ++i) {
        if (e->duty.per_phase[i].charge_mas > worst) {
            worst = e->duty.per_phase[i].charge_mas;
            e->limiter_note = e->duty.per_phase[i].name;
        }
    }
}

est_status lifetime_estimate(const battery_t *b,
                             const duty_cycle_t *dc,
                             const site_t *site,
                             estimate_t *out)
{
    est_status st;

    if (!b || !dc || !site || !out)
        return EST_ERR_NULL;

    st = battery_validate(b);
    if (st != EST_OK)
        return st;
    if (site->cutoff_v <= 0.0 || site->cutoff_v >= b->ocv_fresh_v)
        return EST_ERR_CUTOFF;
    if (site->safety_factor <= 0.0 || site->safety_factor > 1.0)
        return EST_ERR_CAPACITY;

    st = duty_cycle_compute(b, dc, &out->duty);
    if (st != EST_OK)
        return st;

    analyse_pulse(b, site, &out->duty, &out->pulse);

    /* η_cutoff. Пристрій вимикається не тоді, коли OCV дійде до порогу, а
     * тоді, коли ПІД ІМПУЛЬСОМ напруга на клемах провалиться нижче нього.
     * Тож поріг на осі OCV піднятий на всю величину просадки. */
    out->ocv_cutoff_v = site->cutoff_v + out->pulse.sag_v;
    out->eta_cutoff = battery_delivered_above(b, out->ocv_cutoff_v);
    out->eta_temp = battery_temp_factor(b, site->temp_c);
    out->eta_pulse = out->duty.eta_pulse;

    out->c_after_cutoff_mah = b->capacity_mah * out->eta_cutoff;
    out->c_after_temp_mah = out->c_after_cutoff_mah * out->eta_temp;
    out->c_eff_mah = out->c_after_temp_mah * out->eta_pulse;

    out->i_avg_ma = out->duty.i_avg_ma;
    out->i_self_ma = battery_self_discharge_ma(b, site->temp_c);
    out->i_total_ma = out->i_avg_ma + out->i_self_ma;

    if (out->i_total_ma <= 0.0)
        return EST_ERR_NO_DRAIN;

    out->hours = out->c_eff_mah / out->i_total_ma;
    out->days = out->hours / HOURS_PER_DAY;
    out->years = out->days / DAYS_PER_YEAR;
    out->guaranteed_years = out->years * site->safety_factor;

    /* Наївна оцінка з початку статті: паспортна ємність поділена на середній
     * струм, без жодного коефіцієнта зниження. */
    out->naive_years = (b->capacity_mah / out->i_avg_ma) / (HOURS_PER_DAY * DAYS_PER_YEAR);
    out->optimism_ratio = (out->years > 0.0) ? out->naive_years / out->years : INFINITY;

    pick_limiter(out);
    return EST_OK;
}
