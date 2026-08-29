#include "dutycycle.h"

/* Скільки штрафу Пейкерта знімає повний відпочинок комірки між імпульсами:
 * за час сну іони встигають перерозподілитися по об'єму електроліту, і
 * поверхневе виснаження електрода майже повністю розсмоктується. */
#define PEUKERT_RELAX_CREDIT 0.90

static double clampd(double v, double lo, double hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

/* Штраф Пейкерта, послаблений релаксацією. rest_s — час спокою між
 * пробудженнями, relax_s — стала часу дифузійного відновлення комірки. */
static double relaxed_cost(double raw_cost, double rest_s, double relax_s)
{
    double recovery;

    if (raw_cost <= 1.0)
        return 1.0;
    if (relax_s <= 0.0)
        return raw_cost;

    recovery = clampd(rest_s / relax_s, 0.0, 1.0);
    return 1.0 + (raw_cost - 1.0) * (1.0 - PEUKERT_RELAX_CREDIT * recovery);
}

static void fill_phase(dc_phase_result *r, const char *name,
                       double current_ma, double duration_ms,
                       double charge_mas, double cost)
{
    r->name = name;
    r->current_ma = current_ma;
    r->duration_ms = duration_ms;
    r->charge_mas = charge_mas;
    r->peukert_cost = cost;
    r->share = 0.0;
}

est_status duty_cycle_compute(const battery_t *b,
                              const duty_cycle_t *dc,
                              duty_result_t *out)
{
    size_t i;
    double active_s = 0.0;
    double depass_scale = 0.0;
    double depass_dur_s = 0.0;
    double sleep_s;
    double q_peukert = 0.0;
    double cost;

    if (!b || !dc || !out || !dc->phases)
        return EST_ERR_NULL;
    if (dc->count == 0)
        return EST_ERR_NO_PHASES;
    if (dc->count > DC_MAX_PHASES)
        return EST_ERR_TOO_MANY;
    if (dc->period_s <= 0.0)
        return EST_ERR_PERIOD;
    if (dc->sleep_current_ma < 0.0)
        return EST_ERR_PHASE_CURRENT;

    for (i = 0; i < dc->count; ++i) {
        if (dc->phases[i].duration_ms <= 0.0)
            return EST_ERR_PHASE_TIME;
        if (dc->phases[i].current_ma < 0.0)
            return EST_ERR_PHASE_CURRENT;
        active_s += dc->phases[i].duration_ms / 1000.0;
    }

    /* Депасиваційний імпульс має власний, набагато довший період; у баланс
     * одного циклу він входить розмазаною часткою. */
    out->has_depass = 0;
    if (dc->depassivation.duration_ms > 0.0) {
        if (dc->depassivation_period_s <= 0.0)
            return EST_ERR_PERIOD;
        if (dc->depassivation.current_ma < 0.0)
            return EST_ERR_PHASE_CURRENT;
        out->has_depass = 1;
        depass_scale = dc->period_s / dc->depassivation_period_s;
        depass_dur_s = (dc->depassivation.duration_ms / 1000.0) * depass_scale;
    }

    sleep_s = dc->period_s - active_s - depass_dur_s;
    if (sleep_s < 0.0)
        return EST_ERR_PERIOD;   /* пристрій не встигає заснути між пробудженнями */

    out->active_s = active_s;
    out->rest_s = sleep_s;
    out->count = dc->count;
    out->q_active_mas = 0.0;
    out->peak_current_ma = 0.0;
    out->peak_duration_ms = 0.0;
    out->peak_phase = "немає";

    for (i = 0; i < dc->count; ++i) {
        double dur_s = dc->phases[i].duration_ms / 1000.0;
        double q = dc->phases[i].current_ma * dur_s;   /* Q = I · t */

        cost = relaxed_cost(battery_peukert_cost(b, dc->phases[i].current_ma),
                            sleep_s, b->relax_time_s);

        fill_phase(&out->per_phase[i], dc->phases[i].name,
                   dc->phases[i].current_ma, dc->phases[i].duration_ms, q, cost);

        out->q_active_mas += q;
        q_peukert += q * cost;

        if (dc->phases[i].current_ma > out->peak_current_ma) {
            out->peak_current_ma = dc->phases[i].current_ma;
            out->peak_duration_ms = dc->phases[i].duration_ms;
            out->peak_phase = dc->phases[i].name;
        }
    }

    out->q_sleep_mas = dc->sleep_current_ma * sleep_s;
    fill_phase(&out->sleep, "Глибокий сон", dc->sleep_current_ma,
               sleep_s * 1000.0, out->q_sleep_mas, 1.0);
    q_peukert += out->q_sleep_mas;   /* мікроампери беруться нижче еталонного струму */

    out->q_depass_mas = 0.0;
    if (out->has_depass) {
        double q_full = dc->depassivation.current_ma *
                        (dc->depassivation.duration_ms / 1000.0);
        out->q_depass_mas = q_full * depass_scale;
        cost = relaxed_cost(battery_peukert_cost(b, dc->depassivation.current_ma),
                            dc->depassivation_period_s, b->relax_time_s);
        fill_phase(&out->depass, dc->depassivation.name,
                   dc->depassivation.current_ma, dc->depassivation.duration_ms,
                   out->q_depass_mas, cost);
        q_peukert += out->q_depass_mas * cost;
    } else {
        fill_phase(&out->depass, "депасивації немає", 0.0, 0.0, 0.0, 1.0);
    }

    out->q_cycle_mas = out->q_active_mas + out->q_sleep_mas + out->q_depass_mas;
    out->q_cycle_peukert_mas = q_peukert;

    if (out->q_cycle_mas <= 0.0)
        return EST_ERR_NO_DRAIN;

    /* η_pulse — у скільки разів імпульсний характер розряду знецінює
     * паспортну ємність: заряд, узятий струмом 45 мА, коштує дорожче за
     * той самий заряд, узятий мікроамперами. */
    out->eta_pulse = out->q_cycle_mas / out->q_cycle_peukert_mas;
    out->i_avg_ma = out->q_cycle_mas / dc->period_s;

    for (i = 0; i < dc->count; ++i)
        out->per_phase[i].share = out->per_phase[i].charge_mas / out->q_cycle_mas;
    out->sleep.share = out->q_sleep_mas / out->q_cycle_mas;
    if (out->has_depass)
        out->depass.share = out->q_depass_mas / out->q_cycle_mas;

    return EST_OK;
}
