// Задача-зонд: надрукує своє ядро щосекунди
void probe(void *arg) {
    for (;;) {
        Serial.printf("probe runs on core %d\n", xPortGetCoreID());
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void setup() {
    Serial.begin(115200);
    // setup() сама друкує своє ядро — зазвичай 1
    Serial.printf("setup on core %d\n", xPortGetCoreID());

    // probe закріплена на Ядрі 0
    xTaskCreatePinnedToCore(probe, "probe", 2048, NULL, 1, NULL, 0);
}
