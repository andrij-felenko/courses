static TaskHandle_t g_sensor_task_handle = NULL;

void bmp280_dma_complete_isr_hook(bmp280_handle_t *dev) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    /* Виклик внутрішнього обробника компенсації */
    bmp280_dma_complete_callback(dev);

    /* Пряме сповіщення задачі обробки без використання об'єктів семафорів */
    if (g_sensor_task_handle != NULL) {
        vTaskNotifyGiveFromISR(g_sensor_task_handle, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

void vSensorProcessingTask(void *pvParameters) {
    bmp280_handle_t *dev = (bmp280_handle_t*)pvParameters;
    g_sensor_task_handle = xTaskGetCurrentTaskHandle();

    for (;;) {
        /* Запуск неблокуючого зчитування через DMA */
        bmp280_start_read_async_dma(dev);

        /* Задача засинає і не споживає такти CPU, очікуючи сповіщення від DMA ISR */
        uint32_t notification_value = ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(100));

        if (notification_value > 0) {
            /* Дані успішно оновлені в пам'яті */
            bmp280_sample_t sample = dev->last_sample;
            process_barometer_fusion(&sample);
        } else {
            /* Таймаут DMA трансферу: збій шини або обрив зв'язку */
            bmp280_recover_bus(dev);
        }

        vTaskDelay(pdMS_TO_TICKS(20)); /* Період опитування 50 Гц */
    }
}
