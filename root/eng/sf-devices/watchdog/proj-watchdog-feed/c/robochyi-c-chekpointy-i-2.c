void sensor_task(void *arg) {           // швидка задача, строк 200 мс
    for (;;) {
        read_sensor();
        checkpoint(0);                  // відмітились «я жива»
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

void watchdog_task(void *arg) {         // збирач + єдина підписана під TWDT
    esp_task_wdt_add(NULL);
    for (;;) {
        watchdog_collect();
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
