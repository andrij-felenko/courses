#include "moc3063.h"
#include <stddef.h>

/**
 * @brief Допоміжна приватна функція обчислення фізичного рівня GPIO залежно від полярності та стану.
 * 
 * @param active_level Полярність активного сигналу (ACTIVE_HIGH / ACTIVE_LOW).
 * @param state Логічний стан навантаження (MOC3063_STATE_ON / MOC3063_STATE_OFF).
 * @return Фізичний рівень для встановлення на штифті GPIO (true = HIGH, false = LOW).
 */
static bool get_physical_level(moc3063_active_level_t active_level, moc3063_state_t state)
{
    if (active_level == MOC3063_ACTIVE_LOW) {
        /* При Active LOW: ON відповідає LOW (0), OFF відповідає HIGH (1) */
        return (state == MOC3063_STATE_ON) ? false : true;
    } else {
        /* При Active HIGH: ON відповідає HIGH (1), OFF відповідає LOW (0) */
        return (state == MOC3063_STATE_ON) ? true : false;
    }
}

moc3063_status_t moc3063_init(moc3063_t *handle, const moc3063_config_t *config)
{
    if (handle == NULL || config == NULL) {
        return MOC3063_ERROR_INVALID_PARAM;
    }

    if (config->gpio_write == NULL) {
        return MOC3063_ERROR_INVALID_PARAM;
    }

    /* Копіюємо конфігурацію в дескриптор */
    handle->config = *config;
    handle->current_state = config->initial_state;
    handle->is_initialized = false;

    /* Обчислюємо фізичний рівень GPIO для початкового стану */
    bool initial_level = get_physical_level(handle->config.active_level, handle->current_state);

    /* Застосовуємо безпечний початковий рівень на виводі GPIO до позначення ініціалізації */
    handle->config.gpio_write(handle->config.gpio_pin, initial_level);

    handle->is_initialized = true;
    return MOC3063_OK;
}

moc3063_status_t moc3063_set_state(moc3063_t *handle, moc3063_state_t state)
{
    if (handle == NULL || !handle->is_initialized) {
        return MOC3063_ERROR_NOT_INITIALIZED;
    }

    if (state != MOC3063_STATE_OFF && state != MOC3063_STATE_ON) {
        return MOC3063_ERROR_INVALID_PARAM;
    }

    /* Визначаємо потрібний рівень на штифті GPIO */
    bool level = get_physical_level(handle->config.active_level, state);

    /* Передаємо фізичний рівень апаратній функції запису */
    handle->config.gpio_write(handle->config.gpio_pin, level);

    /* Зберігаємо новий логічний стан */
    handle->current_state = state;

    return MOC3063_OK;
}

moc3063_status_t moc3063_turn_on(moc3063_t *handle)
{
    return moc3063_set_state(handle, MOC3063_STATE_ON);
}

moc3063_status_t moc3063_turn_off(moc3063_t *handle)
{
    return moc3063_set_state(handle, MOC3063_STATE_OFF);
}

moc3063_status_t moc3063_toggle(moc3063_t *handle)
{
    if (handle == NULL || !handle->is_initialized) {
        return MOC3063_ERROR_NOT_INITIALIZED;
    }

    moc3063_state_t next_state = (handle->current_state == MOC3063_STATE_ON) 
                                 ? MOC3063_STATE_OFF 
                                 : MOC3063_STATE_ON;

    return moc3063_set_state(handle, next_state);
}

moc3063_status_t moc3063_get_state(const moc3063_t *handle, moc3063_state_t *state)
{
    if (handle == NULL || !handle->is_initialized) {
        return MOC3063_ERROR_NOT_INITIALIZED;
    }

    if (state == NULL) {
        return MOC3063_ERROR_INVALID_PARAM;
    }

    *state = handle->current_state;
    return MOC3063_OK;
}
