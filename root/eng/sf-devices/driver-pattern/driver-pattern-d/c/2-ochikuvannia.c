/* Блокуюча обгортка над асинхронним DMA-рушієм за допомогою сповіщень задачі */
driver_status_t i2c_transfer_rtos_sync(i2c_handle_t* handle, uint8_t addr,
                                       const uint8_t* tx, size_t len) {
    xSemaphoreTake(handle->bus_mutex, portMAX_DELAY);

    handle->calling_task = xTaskGetCurrentTaskHandle();
    driver_status_t st = i2c_master_transfer_async(handle, addr, tx, len, NULL, 0, NULL, NULL);
    if (st == DRIVER_STATUS_OK) {
        /* Задача засинає і віддає CPU іншим потокам */
        uint32_t notify_val = 0;
        if (xTaskNotifyWait(0, ULONG_MAX, &notify_val, pdMS_TO_TICKS(handle->config.timeout_ms)) == pdTRUE) {
            st = (driver_status_t)notify_val;
        } else {
            st = DRIVER_STATUS_TIMEOUT;
        }
    }

    xSemaphoreGive(handle->bus_mutex);
    return st;
}
