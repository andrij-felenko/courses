#include "mosfet_driver.h"
#include <stddef.h>

/**
 * @file mosfet_driver.c
 * @brief Реалізація драйвера силового MOSFET-ключа логічного рівня.
 */

mosfet_status_t mosfet_init(mosfet_driver_t *handle, const mosfet_config_t *config)
{
    if (handle == NULL || config == NULL) {
        return MOSFET_ERROR_INVALID_PARAM;
    }

    /* Обов'язкова наявність низькорівневої функції запису GPIO */
    if (config->gpio_write == NULL) {
        return MOSFET_ERROR_INVALID_PARAM;
    }

    /* Перевірка функції ШІМ, якщо активовано режим ШІМ */
    if (config->use_pwm && config->pwm_set_duty == NULL) {
        return MOSFET_ERROR_INVALID_PARAM;
    }

    handle->config = *config;
    handle->is_initialized = false;
    handle->current_mode = MOSFET_MODE_OFF;
    handle->current_duty_percent = 0;

    /*
     * БЕЗПЕЧНИЙ ЗАПУСК:
     * Першим кроком при ініціалізації гарантовано притискаємо затвор до землі (LOW / 0%),
     * щоб уникнути плаваючого стану затвора під час подачі живлення або перезавантаження МК.
     * Це запобігає самовільному ввімкненню силового навантаження.
     */
    if (handle->config.use_pwm) {
        handle->config.pwm_set_duty(handle->config.pwm_channel, 0);
    }
    handle->config.gpio_write(handle->config.gpio_pin, false);

    handle->is_initialized = true;
    return MOSFET_OK;
}

mosfet_status_t mosfet_safe_shutdown(mosfet_driver_t *handle)
{
    if (handle == NULL || !handle->is_initialized) {
        return MOSFET_ERROR_NOT_INITIALIZED;
    }

    /*
     * Негайне розрядження ємності затвора (C_iss) та притиснення до землі.
     * Транзистор переходить у режим відсічки (High-Z на виході стоку),
     * струм через навантаження припиняється.
     */
    if (handle->config.use_pwm && handle->config.pwm_set_duty != NULL) {
        handle->config.pwm_set_duty(handle->config.pwm_channel, 0);
    }
    handle->config.gpio_write(handle->config.gpio_pin, false);

    handle->current_mode = MOSFET_MODE_OFF;
    handle->current_duty_percent = 0;

    return MOSFET_OK;
}

mosfet_status_t mosfet_set_state(mosfet_driver_t *handle, bool turn_on)
{
    if (handle == NULL || !handle->is_initialized) {
        return MOSFET_ERROR_NOT_INITIALIZED;
    }

    if (!turn_on) {
        return mosfet_safe_shutdown(handle);
    }

    /*
     * ПОВНЕ ВІДКРИТТЯ КЛЮЧА (Насичення):
     * Подача повного логічного рівня (3.3В або 5В) на затвор забезпечує V_GS >> V_GS(th).
     * Канал розтріскується повністю, опір R_DS(on) стає мінімальним (наприклад, 17 мОм для IRLZ44N).
     * Падіння напруги на транзисторі V_DS мінімальне, теплові втрати P = I^2 * R_DS(on) мізерні.
     */
    if (handle->config.use_pwm && handle->config.pwm_set_duty != NULL) {
        handle->config.pwm_set_duty(handle->config.pwm_channel, MOSFET_PWM_MAX_DUTY);
    } else {
        handle->config.gpio_write(handle->config.gpio_pin, true);
    }

    handle->current_mode = MOSFET_MODE_ON;
    handle->current_duty_percent = MOSFET_PWM_MAX_DUTY;

    return MOSFET_OK;
}

mosfet_status_t mosfet_set_duty(mosfet_driver_t *handle, uint8_t duty_percent)
{
    if (handle == NULL || !handle->is_initialized) {
        return MOSFET_ERROR_NOT_INITIALIZED;
    }

    if (!handle->config.use_pwm) {
        return MOSFET_ERROR_PWM_DISABLED;
    }

    if (duty_percent > MOSFET_PWM_MAX_DUTY) {
        return MOSFET_ERROR_INVALID_PARAM;
    }

    if (duty_percent == 0) {
        return mosfet_safe_shutdown(handle);
    }

    if (duty_percent == MOSFET_PWM_MAX_DUTY) {
        return mosfet_set_state(handle, true);
    }

    /*
     * ШІМ-РЕГУЛЮВАННЯ:
     * Швидке перемикання між станами відсічки (0 В) та насичення (VCC).
     * Швидкий фронт нарастання та спаду запобігає затриманню транзистора
     * у лінійній зоні (де V_DS помітне і струм I_D великий, що спричиняє перегрів).
     */
    handle->config.pwm_set_duty(handle->config.pwm_channel, duty_percent);

    handle->current_mode = MOSFET_MODE_PWM;
    handle->current_duty_percent = duty_percent;

    return MOSFET_OK;
}

mosfet_status_t mosfet_get_status(const mosfet_driver_t *handle, mosfet_mode_t *mode, uint8_t *duty_percent)
{
    if (handle == NULL || !handle->is_initialized) {
        return MOSFET_ERROR_NOT_INITIALIZED;
    }

    if (mode != NULL) {
        *mode = handle->current_mode;
    }
    if (duty_percent != NULL) {
        *duty_percent = handle->current_duty_percent;
    }

    return MOSFET_OK;
}

bool mosfet_is_logic_level_compatible(mosfet_drive_voltage_t drive_voltage, uint16_t vgs_th_max_mv)
{
    uint16_t drive_mv = (drive_voltage == MOSFET_DRIVE_3V3) ? 3300 : 5000;

    /*
     * Для повного відкриття ключа логічний рівень керування має перевищувати V_GS(th)_max
     * щонайменше на 1.5 - 2.0 В (зазвичай V_GS = 2 * V_GS(th)).
     * Якщо керуюча напруга близька до V_GS(th), транзистор потрапляє в лінійний режим,
     * опір R_DS різко зростає і ключ сильно гріється під навантаженням.
     */
    return (drive_mv >= (vgs_th_max_mv + 1500));
}
