void motor_control_task(void* pvParameters) {
    auto last_wake_time = xTaskGetTickCount();
    constexpr auto kFrequency = pdMS_TO_TICKS(1);

    for (;;) {
        vTaskDelayUntil(&last_wake_time, kFrequency);

        // 1. Програмний запуск АЦП
        // 2. Розрахунок ПІД
        // 3. Запис у ШІМ
    }
}
