/* app/app_fsm.c — таблиця переходів логера.
 * Жодного включення з hal/ чи bsp/: цей файл компілюється хостовим gcc
 * так само, як кроскомпілятором arm-none-eabi-gcc. */
#include "app/app_fsm.h"

static void enter(app_fsm_t *fsm, app_state_t next, uint32_t now_ms)
{
    if (fsm->state != next) {
        fsm->state = next;
        fsm->state_since_ms = now_ms;
    }
}

void app_fsm_init(app_fsm_t *fsm, uint32_t fault_limit)
{
    if (fsm == 0) {
        return;
    }
    fsm->state              = APP_STATE_BOOT;
    fsm->state_since_ms     = 0u;
    fsm->consecutive_faults = 0u;
    fsm->fault_limit        = (fault_limit == 0u) ? 1u : fault_limit;
}

app_action_t app_fsm_dispatch(app_fsm_t *fsm, const sys_event_t *evt)
{
    if (fsm == 0 || evt == 0) {
        return APP_ACTION_NONE;
    }

    const uint32_t now = evt->timestamp_ms;

    /* Аварія давача рахується в будь-якому стані: одна невдача — випадковість
     * на шині, п'ять поспіль — обрив шлейфа, і про це має знати обслуга. */
    if (evt->id == EVT_ID_SENSOR_FAULT) {
        fsm->consecutive_faults++;
        if (fsm->consecutive_faults >= fsm->fault_limit &&
            fsm->state != APP_STATE_FAULT) {
            enter(fsm, APP_STATE_FAULT, now);
            return APP_ACTION_ENTER_FAULT;
        }
        return APP_ACTION_NONE;
    }

    if (evt->id == EVT_ID_SENSOR_DATA_READY) {
        fsm->consecutive_faults = 0u;
        if (fsm->state == APP_STATE_FAULT) {
            /* Давач ожив — повертаємося до роботи, а не чекаємо перезапуску. */
            enter(fsm, APP_STATE_SAMPLING, now);
            return APP_ACTION_RECOVER;
        }
        return APP_ACTION_NONE;
    }

    switch (fsm->state) {

    case APP_STATE_BOOT:
        if (evt->id == EVT_ID_TICK_100MS) {
            enter(fsm, APP_STATE_SAMPLING, now);
            return APP_ACTION_START_SAMPLING;
        }
        return APP_ACTION_NONE;

    case APP_STATE_IDLE:
        if (evt->id == EVT_ID_BUTTON_CLICK) {
            enter(fsm, APP_STATE_SAMPLING, now);
            return APP_ACTION_START_SAMPLING;
        }
        return APP_ACTION_NONE;

    case APP_STATE_SAMPLING:
        switch (evt->id) {
        case EVT_ID_TICK_100MS:
            return APP_ACTION_SAMPLE_SENSORS;
        case EVT_ID_BUTTON_CLICK:
            enter(fsm, APP_STATE_IDLE, now);
            return APP_ACTION_STOP_SAMPLING;
        case EVT_ID_ALARM_OVERTEMP:
        case EVT_ID_ALARM_VIBRATION:
            enter(fsm, APP_STATE_ALARM, now);
            return APP_ACTION_RAISE_ALARM;
        default:
            return APP_ACTION_NONE;
        }

    case APP_STATE_ALARM:
        switch (evt->id) {
        case EVT_ID_TICK_100MS:
            /* У тривозі вимірювання не спиняються: саме ці дані потім
             * розбиратимуть, коли з'ясовуватимуть причину зупинки насоса. */
            return APP_ACTION_SAMPLE_SENSORS;
        case EVT_ID_ALARM_CLEARED:
            enter(fsm, APP_STATE_SAMPLING, now);
            return APP_ACTION_CLEAR_ALARM;
        default:
            return APP_ACTION_NONE;
        }

    case APP_STATE_FAULT:
        if (evt->id == EVT_ID_TICK_100MS) {
            /* Пробуємо опитати давач знову: гілка виходу зі стану FAULT
             * лежить у обробці EVT_ID_SENSOR_DATA_READY вище. */
            return APP_ACTION_SAMPLE_SENSORS;
        }
        return APP_ACTION_NONE;

    default:
        return APP_ACTION_NONE;
    }
}

app_state_t app_fsm_state(const app_fsm_t *fsm)
{
    return (fsm != 0) ? fsm->state : APP_STATE_BOOT;
}

const char *app_fsm_state_name(app_state_t state)
{
    switch (state) {
    case APP_STATE_BOOT:     return "BOOT";
    case APP_STATE_IDLE:     return "IDLE";
    case APP_STATE_SAMPLING: return "SAMPLING";
    case APP_STATE_ALARM:    return "ALARM";
    case APP_STATE_FAULT:    return "FAULT";
    default:                 return "?";
    }
}

const char *app_fsm_action_name(app_action_t action)
{
    switch (action) {
    case APP_ACTION_NONE:           return "NONE";
    case APP_ACTION_START_SAMPLING: return "START";
    case APP_ACTION_STOP_SAMPLING:  return "STOP";
    case APP_ACTION_SAMPLE_SENSORS: return "SAMPLE";
    case APP_ACTION_RAISE_ALARM:    return "ALARM";
    case APP_ACTION_CLEAR_ALARM:    return "CLEAR";
    case APP_ACTION_ENTER_FAULT:    return "FAULT";
    case APP_ACTION_RECOVER:        return "RECOVER";
    default:                        return "?";
    }
}
