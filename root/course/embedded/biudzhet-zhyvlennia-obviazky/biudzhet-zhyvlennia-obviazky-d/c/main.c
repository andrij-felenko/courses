#include <stdint.h>
#include <stdbool.h>

typedef enum {
    POWER_STATE_DEEP_SLEEP = 0,
    POWER_STATE_SENSOR_ACQ = 1,
    POWER_STATE_PROCESSING = 2,
    POWER_STATE_RADIO_TX   = 3,
    POWER_STATE_COUNT      = 4
} power_state_t;

typedef struct {
    uint32_t state_current_ua[POWER_STATE_COUNT];
    uint32_t state_duration_ms[POWER_STATE_COUNT];
    uint32_t battery_capacity_mah;
    uint32_t battery_self_discharge_ua;
    uint16_t converter_efficiency_pct;
} power_budget_config_t;

typedef struct {
    uint32_t total_cycle_time_ms;
    uint32_t avg_current_ua;
    uint32_t battery_lifetime_hours;
} power_budget_result_t;

bool power_budget_calculate(const power_budget_config_t *cfg, power_budget_result_t *res) {
    if (!cfg || !res || cfg->converter_efficiency_pct == 0) {
        return false;
    }

    uint64_t total_charge_uas = 0;
    uint32_t total_time_ms = 0;

    for (int i = 0; i < POWER_STATE_COUNT; i++) {
        uint64_t state_charge = (uint64_t)cfg->state_current_ua[i] * cfg->state_duration_ms[i];
        total_charge_uas += state_charge;
        total_time_ms += cfg->state_duration_ms[i];
    }

    if (total_time_ms == 0) {
        return false;
    }

    res->total_cycle_time_ms = total_time_ms;
    
    // Середній струм навантаження (мкА)
    uint32_t load_avg_ua = (uint32_t)(total_charge_uas / total_time_ms);

    // Врахування ККД перетворювача та власного саморозряду батареї
    uint32_t effective_draw_ua = (load_avg_ua * 100) / cfg->converter_efficiency_pct;
    effective_draw_ua += cfg->battery_self_discharge_ua;

    res->avg_current_ua = effective_draw_ua;

    if (effective_draw_ua > 0) {
        uint64_t cap_uah = (uint64_t)cfg->battery_capacity_mah * 1000ULL;
        res->battery_lifetime_hours = (uint32_t)(cap_uah / effective_draw_ua);
    } else {
        res->battery_lifetime_hours = 0;
    }

    return true;
}
