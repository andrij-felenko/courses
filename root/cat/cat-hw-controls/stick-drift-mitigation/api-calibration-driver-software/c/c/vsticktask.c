void vStickTask(void *pvParameters) {
    stick_config_t config;
    stick_vector_t vector;
    stick_init(&config);
    
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(10); // 100 Гц
    
    for (;;) {
        uint16_t raw_x = adc_read_x();
        uint16_t raw_y = adc_read_y();
        if (stick_read_normalized(&config, raw_x, raw_y, &vector) == STICK_OK) {
            xQueueSend(xStickQueue, &vector, 0);
        }
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}
