// Поширений перелік статусів помилок драйвера
typedef enum {
    SS41F_STATUS_OK                  =  0,
    SS41F_STATUS_ERR_DEBOUNCE        = -1, // Подію заблоковано фільтром брязкоту
    SS41F_STATUS_ERR_TIMEOUT         = -2, // Тайм-аут: сигнал відсутній занадто довго
    SS41F_STATUS_ERR_FREQ_OVERFLOW   = -3  // Частота перемикань перевищує допустиму
} ss41f_diag_status_t;

// Перевірка стану драйвера на виявлення тайм-ауту зупинки обертання
ss41f_diag_status_t ss41f_check_timeout(const ss41f_driver_t *driver, uint32_t current_time_us, uint32_t timeout_threshold_us) {
    if (driver == NULL || !driver->is_initialized) {
        return SS41F_STATUS_ERR_TIMEOUT;
    }

    uint32_t interval = 0;
    ss41f_get_last_interval(driver, current_time_us, &interval);

    if (interval > timeout_threshold_us) {
        return SS41F_STATUS_ERR_TIMEOUT;
    }

    return SS41F_STATUS_OK;
}
