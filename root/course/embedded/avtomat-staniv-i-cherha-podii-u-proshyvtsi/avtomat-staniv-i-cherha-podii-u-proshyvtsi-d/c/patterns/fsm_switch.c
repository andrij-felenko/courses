#include "fsm_switch.h"

#include "hal.h"

/*
 * Зовнішній switch перемикає стани, внутрішній — розбирає події. Компілятор
 * зазвичай згортає обидва в таблицю переходів асемблера (TBB/TBH на Cortex-M),
 * тож накладних витрат майже немає: ні непрямих викликів, ні таблиць у RAM.
 *
 * Плата за це — дії входу й виходу доводиться виписувати вручну на кожному
 * переході. Нижче на це припадає більша частина коду, і саме тут з'являється
 * найтиповіша помилка патерну: забуте розмикання реле в одній із гілок.
 */

static uint8_t duty_for_current(uint8_t amperes)
{
    if (amperes < 6u) {
        return 0u;
    }
    if (amperes > 51u) {
        amperes = 51u;
    }
    return (uint8_t)(((uint16_t)amperes * 10u + 3u) / 6u);
}

static void enter_standby(sw_fsm_t *fsm)
{
    hal_relay_set(false);
    hal_lock_actuator(false);
    hal_pilot_set_duty(100u);
    hal_led_set(HAL_LED_GREEN, true);
    hal_led_set(HAL_LED_BLUE, false);
    hal_led_set(HAL_LED_RED, false);
    fsm->authorized   = false;
    fsm->lock_engaged = false;
    fsm->state        = SW_ST_STANDBY;
}

static void enter_connected(sw_fsm_t *fsm)
{
    hal_relay_set(false);
    hal_lock_actuator(true);
    hal_pilot_set_duty(duty_for_current(fsm->current_limit_a));
    hal_led_set(HAL_LED_BLUE, false);
    fsm->lock_engaged = true;
    fsm->state        = SW_ST_CONNECTED;
}

static void enter_charging(sw_fsm_t *fsm)
{
    hal_relay_set(true);
    hal_led_set(HAL_LED_BLUE, true);
    fsm->state = SW_ST_CHARGING;
}

static void enter_fault(sw_fsm_t *fsm)
{
    hal_relay_set(false);
    hal_pilot_force_low();
    hal_lock_actuator(false);
    hal_led_set(HAL_LED_GREEN, false);
    hal_led_set(HAL_LED_BLUE, false);
    hal_led_set(HAL_LED_RED, true);
    fsm->authorized   = false;
    fsm->lock_engaged = false;
    fsm->state        = SW_ST_FAULT;
}

void sw_fsm_init(sw_fsm_t *fsm, uint8_t current_limit_a)
{
    fsm->current_limit_a = current_limit_a;
    enter_standby(fsm);
}

void sw_fsm_dispatch(sw_fsm_t *fsm, sw_event_t evt)
{
    switch (fsm->state) {
        case SW_ST_STANDBY:
            switch (evt) {
                case SW_EV_PLUG_IN:
                    enter_connected(fsm);
                    break;
                case SW_EV_OVERCURRENT:
                    enter_fault(fsm);
                    break;
                default:
                    break;
            }
            break;

        case SW_ST_CONNECTED:
            switch (evt) {
                case SW_EV_AUTH_SUCCESS:
                    fsm->authorized = true;
                    break;
                case SW_EV_CHARGE_REQUEST:
                    if (fsm->authorized) {
                        enter_charging(fsm);
                    }
                    break;
                case SW_EV_UNPLUG:
                    enter_standby(fsm);
                    break;
                case SW_EV_OVERCURRENT:
                    enter_fault(fsm);
                    break;
                default:
                    break;
            }
            break;

        case SW_ST_CHARGING:
            switch (evt) {
                case SW_EV_PLUG_IN:
                    /* Автомобіль відпустив ключ: заряджання призупинено.
                     * Реле розмикає enter_connected() — і те саме мусить
                     * зробити кожна інша гілка виходу з CHARGING. */
                    enter_connected(fsm);
                    break;
                case SW_EV_UNPLUG:
                    enter_standby(fsm);
                    break;
                case SW_EV_OVERCURRENT:
                    enter_fault(fsm);
                    break;
                default:
                    break;
            }
            break;

        case SW_ST_FAULT:
            switch (evt) {
                case SW_EV_RESET_BTN:
                    enter_standby(fsm);
                    break;
                default:
                    break;
            }
            break;

        default:
            /* Недосяжна гілка: сюди можна потрапити лише зіпсувавши пам'ять.
             * Безпечна відповідь на зіпсовану пам'ять — знеструмити лінію. */
            enter_fault(fsm);
            break;
    }
}

const char *sw_state_name(sw_state_t s)
{
    switch (s) {
        case SW_ST_STANDBY:   return "STANDBY";
        case SW_ST_CONNECTED: return "CONNECTED";
        case SW_ST_CHARGING:  return "CHARGING";
        case SW_ST_FAULT:     return "FAULT";
        default:              return "?";
    }
}
