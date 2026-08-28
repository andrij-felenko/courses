// FreeRTOS: число пріоритету більше = вищий пріоритет.
// Правило монотонності частоти: тісніший період → вищий пріоритет.
xTaskCreate(motor_task,   "motor",   2048, NULL, 3, NULL);  // 1 мс   — найвищий
xTaskCreate(buttons_task, "buttons", 2048, NULL, 2, NULL);  // 20 мс  — середній
xTaskCreate(display_task, "display", 4096, NULL, 1, NULL);  // 200 мс — найнижчий

void motor_task(void *arg) {
    const TickType_t period = pdMS_TO_TICKS(1);   // строгий ритм 1 мс
    TickType_t next = xTaskGetTickCount();
    for (;;) {
        step_motor();                              // короткий критичний шлях
        vTaskDelayUntil(&next, period);            // прокидатися рівно щомілісекунди
    }
}
