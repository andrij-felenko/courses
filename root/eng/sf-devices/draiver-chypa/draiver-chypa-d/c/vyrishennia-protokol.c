/* Створення м'ютекса з підтримкою Priority Inheritance */
SemaphoreHandle_t g_i2c_bus_mutex = xSemaphoreCreateMutex();

void sensor_thread_safe_read(bmp280_handle_t *dev, bmp280_sample_t *out) {
    /* Захоплення м'ютекса: якщо задачу високого пріоритету заблоковано, 
       пріоритет утримувача м'ютекса тимчасово піднімається до максимального */
    if (xSemaphoreTake(g_i2c_bus_mutex, pdMS_TO_TICKS(50)) == pdTRUE) {
        bmp280_read_sync(dev, out);
        xSemaphoreGive(g_i2c_bus_mutex);
    }
}
