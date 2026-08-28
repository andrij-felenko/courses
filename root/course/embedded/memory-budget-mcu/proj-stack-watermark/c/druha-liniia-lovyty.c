// Ядро викличе це, щойно помітить переповнення стека задачі.
// Ім'я та сигнатура — фіксовані, інакше лінкер не знайде.
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    // У момент виклику стек уже пошкоджено — діяти треба обережно
    // й коротко. Найнадійніше: зафіксувати винного й перезавантажитись.
    taskDISABLE_INTERRUPTS();

    // ім'я задачі-винуватця кладемо в місце, що переживе reset
    // (RTC-пам'ять / noinit-секція), щоб прочитати після перезапуску
    record_fault("STACK OVERFLOW", pcTaskName);

    esp_restart();   // на ESP-IDF; на голому Cortex-M — NVIC_SystemReset()
}
