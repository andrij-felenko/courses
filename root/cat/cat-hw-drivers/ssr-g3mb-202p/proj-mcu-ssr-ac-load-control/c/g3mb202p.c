#include "g3mb202p.h"
#include <stddef.h>

/**
 * @brief Внутрішня приватна функція обчислення апаратного рівня GPIO.
 * 
 * @param active_level Полярність ввімкнення (Active HIGH чи Active LOW).
 * @param state Бажаний стан реле (ON чи OFF).
 * @return Фізичний рівень сигналу на штифті GPIO (true = HIGH, false = LOW).
 */
static bool get_physical_level(g3mb202p_active_level_t active_level, g3mb202p_state_t state)
{
    if (active_level == G3MB202P_ACTIVE_LOW) {
        return (state == G3MB202P_STATE_ON) ? false : true;
    } else {
        return (state == G3MB202P_STATE_ON) ? true : false;
    }
}

g3mb202p_status_t g3mb202p_init(g3mb202p_t *handle, const g3mb202p_config_t *config)
{
    if (handle == NULL || config == NULL) {
        return G3MB202P_ERROR_INVALID_PARAM;
    }

    if (config->gpio_write == NULL) {
        return G3MB202P_ERROR_INVALID_PARAM;
    }

    handle->config = *config;
    handle->current_state = config->initial_state;
    handle->last_switch_time_ms = 0;
    handle->is_initialized = false;

    if (handle->config.get_ms != NULL) {
        handle->last_switch_time_ms = handle->config.get_ms();
    }

    /* Встановлюємо безпечний початковий рівень на цифровому виводі GPIO */
    bool initial_level = get_physical_level(handle->config.active_level, handle->current_state);
    handle->config.gpio_write(handle->config.gpio_pin, initial_level);

    handle->is_initialized = true;
    return G3MB202P_OK;
}

bool g3mb202p_can_switch(const g3mb202p_t *handle)
{
    if (handle == NULL || !handle->is_initialized) {
        return false;
    }

    if (handle->config.get_ms == NULL) {
        /* Якщо системний таймер не підключений, перевірка часового інтервалу пропускається */
        return true;
    }

    uint32_t current_time = handle->config.get_ms();
    uint32_t elapsed = current_time - handle->last_switch_time_ms;

    return (elapsed >= handle->config.min_switch_interval_ms);
}

g3mb202p_status_t g3mb202p_set_state(g3mb202p_t *handle, g3mb202p_state_t state)
{
    if (handle == NULL || !handle->is_initialized) {
        return G3MB202P_ERROR_NOT_INITIALIZED;
    }

    if (state != G3MB202P_STATE_OFF && state != G3MB202P_STATE_ON) {
        return G3MB202P_ERROR_INVALID_PARAM;
    }

    /* Перевіряємо, чи стан вже відповідає запитаному */
    if (handle->current_state == state) {
        return G3MB202P_OK;
    }

    /* Перевірка дотримання часової затримки безпеки між перемиканнями */
    if (!g3mb202p_can_switch(handle)) {
        return G3MB202P_ERROR_THROTTLED;
    }

    /* Обчислюємо та подаємо фізичний логічний рівень на GPIO */
    bool level = get_physical_level(handle->config.active_level, state);
    handle->config.gpio_write(handle->config.gpio_pin, level);

    /* Оновлюємо фіксований стан реле та часовий штамп комутації */
    handle->current_state = state;

    if (handle->config.get_ms != NULL) {
        handle->last_switch_time_ms = handle->config.get_ms();
    }

    /* Якщо надано функцію затримки, витримуємо технологічну паузу Zero-Cross */
    if (handle->config.delay_ms != NULL) {
        handle->config.delay_ms(G3MB202P_ZERO_CROSS_DELAY_MS);
    }

    return G3MB202P_OK;
}

g3mb202p_status_t g3mb202p_turn_on(g3mb202p_t *handle)
{
    return g3mb202p_set_state(handle, G3MB202P_STATE_ON);
}

g3mb202p_status_t g3mb202p_turn_off(g3mb202p_t *handle)
{
    return g3mb202p_set_state(handle, G3MB202P_STATE_OFF);
}

g3mb202p_status_t g3mb202p_toggle(g3mb202p_t *handle)
{
    if (handle == NULL || !handle->is_initialized) {
        return G3MB202P_ERROR_NOT_INITIALIZED;
    }

    g3mb202p_state_t next_state = (handle->current_state == G3MB202P_STATE_ON)
                                 ? G3MB202P_STATE_OFF
                                 : G3MB202P_STATE_ON;

    return g3mb202p_set_state(handle, next_state);
}

g3mb202p_status_t g3mb202p_get_state(const g3mb202p_t *handle, g3mb202p_state_t *state)
{
    if (handle == NULL || !handle->is_initialized) {
        return G3MB202P_ERROR_NOT_INITIALIZED;
    }

    if (state == NULL) {
        return G3MB202P_ERROR_INVALID_PARAM;
    }

    *state = handle->current_state;
    return G3MB202P_OK;
}
