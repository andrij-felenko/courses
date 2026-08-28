// Задача 1: блимати — наче вона сама-одна на процесорі
void blinkTask(void *arg) {
    for (;;) {
        digitalWrite(LED, !digitalRead(LED));
        vTaskDelay(pdMS_TO_TICKS(500));   // «віддай процесор іншим на 500 мс»
    }
}
// Задача 2: обслуговувати мережу — хай блокує скільки треба
void netTask(void *arg) {
    for (;;) {
        handleRequest();                  // 200 мс тут НЕ морозять blinkTask
    }
}
