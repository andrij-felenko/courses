#include "energy_ledger.h"

#include "budget_clock.h"

#include <string.h>

#define MICROSECONDS_PER_HOUR 3600000000ull

static bool phase_valid(energy_phase_t phase)
{
    return (unsigned)phase < (unsigned)ENERGY_PHASE_COUNT;
}

bool energy_ledger_init(energy_ledger_t *ledger,
                        const uint32_t current_ua[ENERGY_PHASE_COUNT])
{
    if (ledger == NULL || current_ua == NULL) {
        return false;
    }
    memset(ledger, 0, sizeof *ledger);
    for (size_t i = 0; i < (size_t)ENERGY_PHASE_COUNT; ++i) {
        ledger->phase_current_ua[i] = current_ua[i];
    }
    ledger->active = ENERGY_PHASE_SLEEP;
    return true;
}

bool energy_ledger_account(energy_ledger_t *ledger, energy_phase_t phase,
                           uint64_t duration_us)
{
    if (ledger == NULL || !phase_valid(phase)) {
        return false;
    }
    if (duration_us == 0u) {
        return true;
    }

    uint64_t charge = (uint64_t)ledger->phase_current_ua[phase] * duration_us;

    ledger->phase_time_us[phase]      += duration_us;
    ledger->phase_charge_ua_us[phase] += charge;
    ledger->total_time_us             += duration_us;
    ledger->total_charge_ua_us        += charge;
    return true;
}

bool energy_ledger_enter(energy_ledger_t *ledger, energy_phase_t phase)
{
    if (ledger == NULL || !phase_valid(phase)) {
        return false;
    }

    uint64_t now = budget_clock_us();
    if (ledger->running) {
        energy_ledger_account(ledger, ledger->active,
                              now - ledger->phase_started_us);
    }
    ledger->active           = phase;
    ledger->phase_started_us = now;
    ledger->running          = true;
    return true;
}

void energy_ledger_stop(energy_ledger_t *ledger)
{
    if (ledger == NULL || !ledger->running) {
        return;
    }
    energy_ledger_account(ledger, ledger->active,
                          budget_clock_us() - ledger->phase_started_us);
    ledger->running = false;
}

uint32_t energy_ledger_avg_current_ua(const energy_ledger_t *ledger)
{
    if (ledger == NULL || ledger->total_time_us == 0u) {
        return 0u;
    }
    return (uint32_t)(ledger->total_charge_ua_us / ledger->total_time_us);
}

uint32_t energy_ledger_charge_uah(const energy_ledger_t *ledger)
{
    if (ledger == NULL) {
        return 0u;
    }
    return (uint32_t)(ledger->total_charge_ua_us / MICROSECONDS_PER_HOUR);
}

uint32_t energy_ledger_share_pm(const energy_ledger_t *ledger,
                                energy_phase_t phase)
{
    if (ledger == NULL || !phase_valid(phase) ||
        ledger->total_charge_ua_us == 0u) {
        return 0u;
    }
    return (uint32_t)(ledger->phase_charge_ua_us[phase] * 1000u /
                      ledger->total_charge_ua_us);
}

uint32_t energy_ledger_time_share_pm(const energy_ledger_t *ledger,
                                     energy_phase_t phase)
{
    if (ledger == NULL || !phase_valid(phase) || ledger->total_time_us == 0u) {
        return 0u;
    }
    return (uint32_t)(ledger->phase_time_us[phase] * 1000u /
                      ledger->total_time_us);
}

uint32_t energy_ledger_life_hours(const energy_ledger_t *ledger,
                                  uint32_t battery_mah)
{
    uint32_t avg_ua = energy_ledger_avg_current_ua(ledger);
    if (avg_ua == 0u) {
        return UINT32_MAX; /* витрати нижчі за роздільність обліку */
    }
    return (uint32_t)((uint64_t)battery_mah * 1000u / avg_ua);
}

budget_flags_t energy_ledger_audit(const energy_ledger_t *ledger,
                                   uint32_t battery_mah,
                                   uint32_t required_hours)
{
    if (ledger == NULL || ledger->total_time_us == 0u) {
        return BUDGET_OK; /* поки нічого не виміряно, судити нема про що */
    }
    return (energy_ledger_life_hours(ledger, battery_mah) < required_hours)
               ? BUDGET_ENERGY_OVER
               : BUDGET_OK;
}

const char *energy_phase_name(energy_phase_t phase)
{
    switch (phase) {
    case ENERGY_PHASE_SLEEP:   return "глибокий сон";
    case ENERGY_PHASE_SENSE:   return "опитування сенсорів";
    case ENERGY_PHASE_PROCESS: return "обробка та шифрування";
    case ENERGY_PHASE_TX:      return "радіопередача";
    default:                   return "?";
    }
}
