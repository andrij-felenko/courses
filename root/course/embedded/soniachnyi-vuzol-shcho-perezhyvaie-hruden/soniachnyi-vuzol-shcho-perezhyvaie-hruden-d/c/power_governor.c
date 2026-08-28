/* power_governor.c - Реалізація логіки автомата станів на C99 */
#include "power_governor.h"

void power_governor_init(power_governor_t *gov, const power_config_t *cfg) {
    if (!gov || !cfg) return;
    gov->config = *cfg;
    gov->current_state = POWER_STATE_NORMAL;
    gov->soak_counter_s = 0;
    gov->charge_enabled = true;
    gov->sensors_enabled = true;
    gov->radio_enabled = true;
}

void power_governor_update(power_governor_t *gov, const power_telemetry_t *telem, uint32_t elapsed_s) {
    if (!gov || !telem) return;

    /* 1. Температурний захист від літієвого платування */
    gov->charge_enabled = (telem->temp_celsius >= gov->config.temp_charge_min_c);

    /* 2. Скінченний автомат керування живленням */
    switch (gov->current_state) {
        case POWER_STATE_NORMAL:
            gov->sensors_enabled = true;
            gov->radio_enabled = true;
            if (telem->voltage_mv <= gov->config.v_normal_mv) {
                gov->current_state = POWER_STATE_ECO;
            }
            break;

        case POWER_STATE_ECO:
            gov->sensors_enabled = true;
            gov->radio_enabled = true;
            if (telem->voltage_mv > (gov->config.v_normal_mv + gov->config.v_hysteresis_mv)) {
                gov->current_state = POWER_STATE_NORMAL;
            } else if (telem->voltage_mv <= gov->config.v_eco_mv) {
                gov->current_state = POWER_STATE_SURVIVAL;
            }
            break;

        case POWER_STATE_SURVIVAL:
            gov->sensors_enabled = false; /* Знеструмлення зовнішніх сенсорів */
            gov->radio_enabled = true;    /* Дозволено лише короткий маяк */
            if (telem->voltage_mv > (gov->config.v_eco_mv + gov->config.v_hysteresis_mv)) {
                gov->current_state = POWER_STATE_ECO;
            } else if (telem->voltage_mv <= gov->config.v_hibernate_mv) {
                gov->current_state = POWER_STATE_HIBERNATE;
                gov->soak_counter_s = 0;
            }
            break;

        case POWER_STATE_HIBERNATE:
            gov->sensors_enabled = false;
            gov->radio_enabled = false; /* Радіо повністю вимкнено */
            if ((telem->voltage_mv >= (gov->config.v_hibernate_mv + gov->config.v_hysteresis_mv)) &&
                (telem->charge_current_ma > 10)) {
                gov->current_state = POWER_STATE_RECOVERY;
                gov->soak_counter_s = 0;
            }
            break;

        case POWER_STATE_RECOVERY:
            gov->sensors_enabled = false;
            gov->radio_enabled = false;
            if (telem->charge_current_ma > 15) {
                gov->soak_counter_s += elapsed_s;
            } else {
                gov->soak_counter_s = 0;
            }

            if ((telem->voltage_mv >= gov->config.v_recovery_mv) &&
                (gov->soak_counter_s >= gov->config.soak_time_req_s)) {
                gov->current_state = POWER_STATE_ECO;
                gov->soak_counter_s = 0;
            } else if (telem->voltage_mv < gov->config.v_hibernate_mv) {
                gov->current_state = POWER_STATE_HIBERNATE;
            }
            break;
    }
}

uint32_t power_governor_get_sleep_seconds(const power_governor_t *gov) {
    if (!gov) return 300;
    switch (gov->current_state) {
        case POWER_STATE_NORMAL:    return 300;   /* 5 хвилин */
        case POWER_STATE_ECO:       return 2700;  /* 45 хвилин */
        case POWER_STATE_SURVIVAL:  return 28800; /* 8 годин */
        case POWER_STATE_HIBERNATE: return 86400; /* 24 години */
        case POWER_STATE_RECOVERY:  return 1800;  /* 30 хвилин */
        default:                    return 300;
    }
}
