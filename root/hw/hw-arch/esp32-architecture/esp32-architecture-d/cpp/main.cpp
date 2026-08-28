// ESP-IDF / Arduino-ESP32: остання цифра — номер ядра (0 або 1)
void worker(void *arg) {
    for (;;) {
        printf("рахую на ядрі %d\n", xPortGetCoreID());   // → 1
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void app_main(void) {
    xTaskCreatePinnedToCore(
        worker, "worker",
        4096,   // стек задачі, байтів
        NULL, 5,
        NULL,
        1);     // APP_CPU_NUM — закріпити за ядром 1
}
