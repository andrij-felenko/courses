void MotorControlTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(1); /* 1 кГц */

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
        
        /* 1. Програмний запуск АЦП */
        /* 2. Розрахунок ПІД */
        /* 3. Запис у ШІМ */
    }
}
