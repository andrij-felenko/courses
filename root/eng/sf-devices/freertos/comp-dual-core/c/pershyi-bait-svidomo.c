void taskCtrl(void *p) {
    // перший рядок — підтвердження розміщення
    Serial.printf("ctrl runs on core %d\n", xPortGetCoreID());
    for (;;) {
        // критичний крок: керування, генерація сигналу, тайм-критичне опитування
        vTaskDelay(1);  // завжди поступатися, щоб IDLE встигала годувати watchdog
    }
}

void setup() {
    Serial.begin(115200);
    // xTaskCreatePinnedToCore(fn, name, stack_bytes, param, prio, handle, coreID)
    // stack — у байтах на ESP32 (не у словах, як у класичному FreeRTOS)
    xTaskCreatePinnedToCore(taskCtrl, "ctrl", 4096, NULL, 2, NULL, 1);
}
