/* Потокобезпечний запис у Flash під керуванням FreeRTOS (C) */
bool qspi_threadsafe_write(uint32_t addr, const uint8_t *data, size_t len) {
    extern SemaphoreHandle_t qspi_mutex;

    /* Захоплення м'ютекса для блокування інших задач */
    if (xSemaphoreTake(qspi_mutex, portMAX_DELAY) != pdTRUE) {
        return false;
    }

    /* Безпечне виконання операції з тимчасовим виходом із XIP */
    safe_flash_page_program(addr, data, len);

    /* Звільнення м'ютекса */
    xSemaphoreGive(qspi_mutex);
    return true;
}
