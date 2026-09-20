#include "apc_laser_controller.h"
#include <stddef.h>

/**
 * @file apc_laser_controller.c
 * @brief Реалізація драйвера нижнього рівня для керування лазерним діодом.
 */

/* Низькорівнева апаратна абстракція (HAL-функції з можливістю перевизначення) */

__attribute__((weak)) void hal_gpio_write_pin(uint8_t port, uint16_t pin, bool state) {
    (void)port;
    (void)pin;
    (void)state;
}

__attribute__((weak)) void hal_dac_write_value(uint8_t channel, uint16_t raw_val) {
    (void)channel;
    (void)raw_val;
}

__attribute__((weak)) uint16_t hal_adc_read_value(uint8_t channel) {
    (void)channel;
    return 0;
}

__attribute__((weak)) void hal_delay_ms(uint32_t ms) {
    (void)ms;
}

/* Реалізація публічних функцій драйвера */

apc_status_t apc_laser_init(apc_driver_t *driver, const apc_config_t *config) {
    if (driver == NULL || config == NULL) {
        return APC_ERROR_INVALID_PARAM;
    }

    /* Перевірка коректності конфігураційних меж */
    if (config->max_pd_adc_raw == 0 ||
        config->target_pd_adc_raw > config->max_pd_adc_raw ||
        config->soft_start_step == 0 ||
        config->dac_max_limit == 0) {
        return APC_ERROR_INVALID_PARAM;
    }

    driver->config = *config;
    driver->state = APC_STATE_DISABLED;
    driver->current_dac_val = 0;
    driver->last_adc_raw = 0;
    driver->integral_error = 0;
    driver->last_error = APC_OK;
    driver->is_initialized = true;

    /* Гарантований безпечний стан при ініціалізації */
    hal_dac_write_value(driver->config.hw.dac_channel, 0);
    hal_gpio_write_pin(driver->config.hw.gpio_enable_port, driver->config.hw.gpio_enable_pin, false);

    return APC_OK;
}

apc_status_t apc_laser_disable(apc_driver_t *driver) {
    if (driver == NULL) {
        return APC_ERROR_INVALID_PARAM;
    }

    /* Скидаємо вихід ЦАП у нуль і деактивуємо Enable для безпеки */
    hal_dac_write_value(driver->config.hw.dac_channel, 0);
    hal_gpio_write_pin(driver->config.hw.gpio_enable_port, driver->config.hw.gpio_enable_pin, false);

    driver->current_dac_val = 0;
    driver->integral_error = 0;

    if (driver->state != APC_STATE_FAULT) {
        driver->state = APC_STATE_DISABLED;
    }

    return APC_OK;
}

bool apc_laser_check_protection(apc_driver_t *driver) {
    if (driver == NULL || !driver->is_initialized) {
        return false;
    }

    /* Зчитуємо поточне значення з моніторного фотодіода */
    uint16_t adc_val = hal_adc_read_value(driver->config.hw.adc_pd_channel);
    driver->last_adc_raw = adc_val;

    /* Якщо зчитане значення перевищує максимальну межу — захист спрацьовує */
    if (adc_val > driver->config.max_pd_adc_raw) {
        return false;
    }

    return true;
}

apc_status_t apc_laser_soft_start(apc_driver_t *driver) {
    if (driver == NULL || !driver->is_initialized) {
        return APC_ERROR_NOT_INITIALIZED;
    }

    driver->state = APC_STATE_SOFT_START;
    driver->integral_error = 0;

    /* Увімкнення силового ключа */
    hal_gpio_write_pin(driver->config.hw.gpio_enable_port, driver->config.hw.gpio_enable_pin, true);

    /* Покрокове збільшення напруги ЦАП для відсутності кидатків струму */
    while (driver->current_dac_val < driver->config.dac_max_limit) {
        uint32_t next_dac = (uint32_t)driver->current_dac_val + driver->config.soft_start_step;
        if (next_dac > driver->config.dac_max_limit) {
            next_dac = driver->config.dac_max_limit;
        }

        driver->current_dac_val = (uint16_t)next_dac;
        hal_dac_write_value(driver->config.hw.dac_channel, driver->current_dac_val);

        hal_delay_ms(driver->config.soft_start_delay_ms);

        /* Контроль оптичного відгуку на кожному кроці пуску */
        if (!apc_laser_check_protection(driver)) {
            apc_laser_disable(driver);
            driver->state = APC_STATE_FAULT;
            driver->last_error = APC_ERROR_OVERCURRENT;
            return APC_ERROR_OVERCURRENT;
        }

        /* Досягнення цільової оптичної потужності зупиняє розгін */
        if (driver->last_adc_raw >= driver->config.target_pd_adc_raw) {
            break;
        }
    }

    driver->state = APC_STATE_RUNNING;
    return APC_OK;
}

apc_status_t apc_laser_update_apc(apc_driver_t *driver) {
    if (driver == NULL || !driver->is_initialized) {
        return APC_ERROR_NOT_INITIALIZED;
    }

    if (driver->state != APC_STATE_RUNNING) {
        return APC_OK;
    }

    /* Моніторинг захисту перед розрахунком регулятора */
    if (!apc_laser_check_protection(driver)) {
        apc_laser_disable(driver);
        driver->state = APC_STATE_FAULT;
        driver->last_error = APC_ERROR_OVERCURRENT;
        return APC_ERROR_OVERCURRENT;
    }

    /* Розрахунок помилки регулювання: (Ціль - Поточне значення фотодіода) */
    int32_t error = (int32_t)driver->config.target_pd_adc_raw - (int32_t)driver->last_adc_raw;

    /* Обмеження накопичення інтегральної помилки (Anti-windup) */
    driver->integral_error += error;
    if (driver->integral_error > 4000) {
        driver->integral_error = 4000;
    } else if (driver->integral_error < -4000) {
        driver->integral_error = -4000;
    }

    /* ПІ-регулятор струму накачки */
    int32_t p_term = (error * (int32_t)driver->config.kp_gain) / 10;
    int32_t i_term = (driver->integral_error * (int32_t)driver->config.ki_gain) / 100;

    int32_t new_dac = (int32_t)driver->current_dac_val + p_term + i_term;

    /* Обмеження діапазону виходу ЦАП */
    if (new_dac < 0) {
        new_dac = 0;
    } else if (new_dac > (int32_t)driver->config.dac_max_limit) {
        new_dac = driver->config.dac_max_limit;
    }

    driver->current_dac_val = (uint16_t)new_dac;
    hal_dac_write_value(driver->config.hw.dac_channel, driver->current_dac_val);

    return APC_OK;
}

apc_status_t apc_laser_set_target(apc_driver_t *driver, uint16_t target_adc_raw) {
    if (driver == NULL || !driver->is_initialized) {
        return APC_ERROR_NOT_INITIALIZED;
    }

    if (target_adc_raw > driver->config.max_pd_adc_raw) {
        return APC_ERROR_INVALID_PARAM;
    }

    driver->config.target_pd_adc_raw = target_adc_raw;
    return APC_OK;
}

apc_state_t apc_laser_get_state(const apc_driver_t *driver) {
    if (driver == NULL) {
        return APC_STATE_DISABLED;
    }
    return driver->state;
}
