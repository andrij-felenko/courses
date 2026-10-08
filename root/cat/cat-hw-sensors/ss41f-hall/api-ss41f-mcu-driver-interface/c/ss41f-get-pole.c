// Отримання поточного логічного стану давача SS41F
ss41f_pole_t ss41f_get_pole(const ss41f_driver_t *driver) {
    if (driver == NULL || !driver->is_initialized) {
        return SS41F_POLE_UNKNOWN;
    }
    return driver->current_pole;
}

// Отримання тривалості останнього інтервалу між перемиканнями у мікросекундах
ss41f_status_t ss41f_get_last_interval(const ss41f_driver_t *driver, uint32_t current_time_us, uint32_t *out_interval_us) {
    if (driver == NULL || out_interval_us == NULL || !driver->is_initialized) {
        return SS41F_ERR_INVALID_ARG;
    }

    uint32_t last_time = driver->last_change_us;
    if (last_time == 0) {
        *out_interval_us = 0; // Подій ще не було
        return SS41F_OK;
    }

    // Обчислення різниці з урахуванням можливого переповнення 32-бітного лічильника
    if (current_time_us >= last_time) {
        *out_interval_us = current_time_us - last_time;
    } else {
        *out_interval_us = (0xFFFFFFFF - last_time) + current_time_us + 1;
    }

    return SS41F_OK;
}
