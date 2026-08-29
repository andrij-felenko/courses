#include "thermal_budget.h"

#include <string.h>

/*
 * Перегрів у десятих градуса:
 *   dT[°C]  = P[Вт] * R[°C/Вт] = (P_mW / 1000) * (R_mcw / 1000)
 *   dT[dC] = P_mW * R_mcw / 100000
 */
#define THERMAL_SCALE 100000ull

bool thermal_monitor_init(thermal_monitor_t *tm, const thermal_limits_t *limits)
{
    if (tm == NULL || limits == NULL || limits->rth_ja_mcw == 0u) {
        return false;
    }
    memset(tm, 0, sizeof *tm);
    tm->limits  = *limits;
    tm->peak_dc = INT16_MIN;
    return true;
}

int16_t thermal_junction_dc(int16_t ambient_dc, uint32_t power_mw,
                            uint32_t rth_ja_mcw)
{
    uint64_t rise = ((uint64_t)power_mw * rth_ja_mcw) / THERMAL_SCALE;
    int64_t  tj   = (int64_t)ambient_dc + (int64_t)rise;

    if (tj > INT16_MAX) {
        return INT16_MAX;
    }
    return (int16_t)tj;
}

uint32_t thermal_max_power_mw(const thermal_limits_t *limits, int16_t ambient_dc)
{
    if (limits == NULL || limits->rth_ja_mcw == 0u) {
        return 0u;
    }

    int32_t delta_dc = (int32_t)limits->tj_max_dc - (int32_t)ambient_dc;
    if (delta_dc <= 0) {
        /* Середовище вже гарячіше за допустиму температуру кристала. */
        return 0u;
    }
    return (uint32_t)(((uint64_t)delta_dc * THERMAL_SCALE) / limits->rth_ja_mcw);
}

uint32_t thermal_ldo_max_current_ma(const thermal_limits_t *limits,
                                    int16_t ambient_dc, uint32_t dropout_mv)
{
    if (dropout_mv == 0u) {
        return 0u;
    }
    /* I[мА] = P[мВт] * 1000 / U[мВ] */
    uint64_t p_mw = thermal_max_power_mw(limits, ambient_dc);
    return (uint32_t)(p_mw * 1000u / dropout_mv);
}

budget_flags_t thermal_monitor_sample(thermal_monitor_t *tm, int16_t ambient_dc,
                                      uint32_t power_mw)
{
    if (tm == NULL) {
        return BUDGET_THERMAL_TRIP;
    }

    tm->ambient_dc  = ambient_dc;
    tm->power_mw    = power_mw;
    tm->junction_dc =
        thermal_junction_dc(ambient_dc, power_mw, tm->limits.rth_ja_mcw);

    if (tm->junction_dc > tm->peak_dc) {
        tm->peak_dc = tm->junction_dc;
    }

    const int16_t warn_dc =
        (int16_t)(tm->limits.tj_max_dc - tm->limits.warn_margin_dc);

    if (tm->junction_dc >= tm->limits.tj_max_dc) {
        tm->trip_events++;
        tm->throttled = true;
        return BUDGET_THERMAL_TRIP | BUDGET_THERMAL_WARN;
    }

    if (tm->junction_dc >= warn_dc) {
        tm->throttled = true;
        return BUDGET_THERMAL_WARN;
    }

    /*
     * Тривогу знімаємо лише з гістерезисом: без нього вузол смикався б між
     * повним і зниженим навантаженням на кожному відліку.
     */
    if (tm->throttled &&
        tm->junction_dc < (int16_t)(warn_dc - tm->limits.hysteresis_dc)) {
        tm->throttled = false;
    }

    return tm->throttled ? BUDGET_THERMAL_WARN : BUDGET_OK;
}
