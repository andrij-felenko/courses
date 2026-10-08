/**
 * @file hc_sr505.c
 * @brief Реалізація високорівневої логіки драйвера PIR-давача руху HC-SR505.
 *
 * Реалізує обробку цифрового сигналу від HC-SR505, керування виходом MOSFET,
 * проходження станів ACTIVE -> COOLDOWN -> IDLE та координацію переходу в глибокий сон.
 */

#include "hc_sr505.h"
#include "mcu_power_exti.h"
#include <stdio.h>

hc_sr505_status_t hc_sr505_init(hc_sr505_t *dev, const hc_sr505_config_t *config)
{
    if (dev == NULL || config == NULL) {
        return HC_SR505_ERR_NULL_PTR;
    }

    if (config->active_hold_ms == 0) {
        return HC_SR505_ERR_INVALID_PARAM;
    }

    dev->config = *config;
    dev->state = PIR_STATE_IDLE;
    dev->motion_raw_signal = false;
    dev->mosfet_gate_active = false;
    dev->motion_trigger_count = 0;
    dev->last_trigger_timestamp_ms = 0;
    dev->state_entry_time_ms = mcu_get_tick_ms();

    /* Примусово переводимо затвор MOSFET у безпечний вимкнений стан (LOW) */
    mcu_gpio_write_mosfet_pin(false);

    return HC_SR505_OK;
}

hc_sr505_status_t hc_sr505_on_motion_isr(hc_sr505_t *dev)
{
    if (dev == NULL) {
        return HC_SR505_ERR_NULL_PTR;
    }

    uint32_t now = mcu_get_tick_ms();
    dev->motion_trigger_count++;
    dev->last_trigger_timestamp_ms = now;
    dev->motion_raw_signal = true;

    /* Зміна стану на виявлений рух при спрацьовуванні апаратного EXTI переривання */
    if (dev->state == PIR_STATE_IDLE || dev->state == PIR_STATE_COOLDOWN) {
        dev->state = PIR_STATE_MOTION_DETECTED;
        dev->state_entry_time_ms = now;
    }

    return HC_SR505_OK;
}

hc_sr505_status_t hc_sr505_read_raw_pin(hc_sr505_t *dev, bool *pin_state)
{
    if (dev == NULL || pin_state == NULL) {
        return HC_SR505_ERR_NULL_PTR;
    }

    bool level = mcu_gpio_read_pir_pin();
    dev->motion_raw_signal = (level == dev->config.active_high_logic);
    *pin_state = dev->motion_raw_signal;

    return HC_SR505_OK;
}

hc_sr505_status_t hc_sr505_set_mosfet(hc_sr505_t *dev, bool enable)
{
    if (dev == NULL) {
        return HC_SR505_ERR_NULL_PTR;
    }

    dev->mosfet_gate_active = enable;
    mcu_gpio_write_mosfet_pin(enable);

    return HC_SR505_OK;
}

hc_sr505_status_t hc_sr505_process(hc_sr505_t *dev, uint32_t current_time_ms)
{
    if (dev == NULL) {
        return HC_SR505_ERR_NULL_PTR;
    }

    bool raw_pin = false;
    hc_sr505_read_raw_pin(dev, &raw_pin);

    switch (dev->state) {
    case PIR_STATE_IDLE:
        /* У стані спокою MOSFET вимкнений. Якщо МК активний і включено auto_sleep, переходимо в сон */
        if (dev->mosfet_gate_active) {
            hc_sr505_set_mosfet(dev, false);
        }
        if (dev->config.auto_sleep_enable) {
            mcu_power_enter_deep_sleep();
        }
        break;

    case PIR_STATE_MOTION_DETECTED:
        /* Реакція на виявлення руху: вмикаємо силовий MOSFET */
        hc_sr505_set_mosfet(dev, true);
        dev->state = PIR_STATE_LOAD_ACTIVE;
        dev->state_entry_time_ms = current_time_ms;
        break;

    case PIR_STATE_LOAD_ACTIVE:
        /* Поки давач HC-SR505 утримує HIGH рівень, продовжуємо вікно активності */
        if (raw_pin) {
            dev->state_entry_time_ms = current_time_ms;
        } else {
            /* Сигнал давача впав у LOW, перевіряємо витримку active_hold_ms */
            if ((current_time_ms - dev->state_entry_time_ms) >= dev->config.active_hold_ms) {
                hc_sr505_set_mosfet(dev, false);
                dev->state = PIR_STATE_COOLDOWN;
                dev->state_entry_time_ms = current_time_ms;
            }
        }
        break;

    case PIR_STATE_COOLDOWN:
        /* Очікування завершення періоду стабілізації */
        if (raw_pin) {
            /* Якщо під час стабілізації повторно з'явився рух, повертаємось до активного навантаження */
            hc_sr505_set_mosfet(dev, true);
            dev->state = PIR_STATE_LOAD_ACTIVE;
            dev->state_entry_time_ms = current_time_ms;
        } else if ((current_time_ms - dev->state_entry_time_ms) >= dev->config.cooldown_ms) {
            dev->state = PIR_STATE_IDLE;
            dev->state_entry_time_ms = current_time_ms;
        }
        break;

    case PIR_STATE_ERROR:
    default:
        hc_sr505_set_mosfet(dev, false);
        break;
    }

    return HC_SR505_OK;
}

pir_state_t hc_sr505_get_state(const hc_sr505_t *dev)
{
    if (dev == NULL) {
        return PIR_STATE_ERROR;
    }
    return dev->state;
}

const char* hc_sr505_state_to_str(pir_state_t state)
{
    switch (state) {
    case PIR_STATE_IDLE:            return "IDLE (Сон, навантаження OFF)";
    case PIR_STATE_MOTION_DETECTED: return "MOTION_DETECTED (Фіксація руху)";
    case PIR_STATE_LOAD_ACTIVE:     return "LOAD_ACTIVE (Навантаження ON)";
    case PIR_STATE_COOLDOWN:        return "COOLDOWN (Стабілізація)";
    case PIR_STATE_ERROR:           return "ERROR (Помилка)";
    default:                        return "UNKNOWN";
    }
}
