#include "rail_monitor.h"

#include <string.h>

bool rail_monitor_init(rail_monitor_t *rail, const rail_limits_t *limits)
{
    if (rail == NULL || limits == NULL) {
        return false;
    }
    if (limits->bor_mv >= limits->warn_mv || limits->warn_mv > limits->nominal_mv) {
        return false;
    }

    memset(rail, 0, sizeof *rail);
    rail->limits = *limits;
    rail->min_mv = limits->nominal_mv;
    rail->last_mv = limits->nominal_mv;
    return true;
}

budget_flags_t rail_monitor_sample(rail_monitor_t *rail, uint16_t millivolts)
{
    if (rail == NULL) {
        return BUDGET_VDD_BROWNOUT;
    }

    rail->last_mv = millivolts;
    rail->samples++;
    if (millivolts < rail->min_mv) {
        rail->min_mv = millivolts;
    }

    if (millivolts <= rail->limits.bor_mv) {
        rail->brownout_events++;
        return BUDGET_VDD_BROWNOUT | BUDGET_VDD_SAG;
    }
    if (millivolts < rail->limits.warn_mv) {
        rail->sag_events++;
        return BUDGET_VDD_SAG;
    }
    return BUDGET_OK;
}

int32_t rail_monitor_headroom_mv(const rail_monitor_t *rail)
{
    if (rail == NULL) {
        return 0;
    }
    return (int32_t)rail->min_mv - (int32_t)rail->limits.bor_mv;
}

uint32_t rail_estimate_droop_mv(uint32_t peak_ma, uint32_t esr_mohm,
                                uint32_t bulk_uf, uint32_t burst_us)
{
    /* мА * мОм / 1000 = мВ */
    uint64_t esr_drop_mv = (uint64_t)peak_ma * esr_mohm / 1000u;

    /* мА * мкс / мкФ = мВ (одиниці скорочуються рівно) */
    uint64_t discharge_mv = 0u;
    if (bulk_uf > 0u) {
        discharge_mv = (uint64_t)peak_ma * burst_us / bulk_uf;
    } else {
        discharge_mv = UINT32_MAX; /* без буферної ємності просідання не обмежене */
    }

    uint64_t total = esr_drop_mv + discharge_mv;
    return (total > UINT32_MAX) ? UINT32_MAX : (uint32_t)total;
}
