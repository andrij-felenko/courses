// Виклик обробника переривань EXTI для давача SS41F
void ss41f_isr_handler(ss41f_driver_t *driver, uint32_t current_time_us, bool pin_level_high) {
    if (driver == NULL || !driver->is_initialized) {
        return;
    }

    // Перевірка часового вікна брязкоту
    uint32_t delta = current_time_us - driver->last_change_us;
    if (driver->last_change_us != 0 && delta < driver->config.debounce_window_us) {
        return; // Ігноруємо надто часті перемикання (завади)
    }

    // Визначення нового полюса за логічним рівнем виходу SS41F
    ss41f_pole_t new_pole = pin_level_high ? SS41F_POLE_NORTH : SS41F_POLE_SOUTH;

    // Оновлення стану драйвера
    driver->current_pole = new_pole;
    driver->last_change_us = current_time_us;
    driver->event_count++;

    // Виклик асинхронного callback користувача
    if (driver->config.callback != NULL) {
        driver->config.callback(new_pole, current_time_us, driver->config.user_data);
    }
}
