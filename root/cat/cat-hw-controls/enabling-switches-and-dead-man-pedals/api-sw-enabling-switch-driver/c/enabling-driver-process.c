// Періодичне опитування та оновлення стану драйвера (викликається кожні 1 мс)
enabling_state_t enabling_driver_process(enabling_driver_t *driver, uint16_t tick_ms) {
    if (!driver) return ENABLING_STATE_FAULT;

    bool raw_a = driver->config.read_ch_a();
    bool raw_b = driver->config.read_ch_b();

    // Перевірка збігу каналів
    if (raw_a == raw_b) {
        driver->discrepancy_timer = 0;
        if (!raw_a) {
            // Обидва 0: Released або Panic залежно від попереднього руху
            if (driver->current_state == ENABLING_STATE_ENABLED) {
                driver->current_state = ENABLING_STATE_PANIC;
            } else if (driver->current_state != ENABLING_STATE_PANIC) {
                driver->current_state = ENABLING_STATE_RELEASED;
            }
        } else {
            // Обидва 1: Enabled (дозволено лише з Released)
            if (driver->current_state == ENABLING_STATE_RELEASED || driver->current_state == ENABLING_STATE_ENABLED) {
                driver->current_state = ENABLING_STATE_ENABLED;
            }
        }
    } else {
        // Розсинхронізм каналів: відлік таймера discrepancy
        driver->discrepancy_timer += tick_ms;
        if (driver->discrepancy_timer >= driver->config.discrepancy_ms) {
            driver->current_state = ENABLING_STATE_FAULT;
        }
    }

    return driver->current_state;
}
