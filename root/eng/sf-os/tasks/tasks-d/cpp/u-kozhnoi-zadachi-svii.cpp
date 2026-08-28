void taskCounter(void *p) {
    int n = 0;                         // локальна змінна — лежить у СТЕКУ цієї задачі
    const char *name = (const char *)p;
    for (;;) {
        n++;                           // рахуємо
        Serial.printf("%s: n=%d\n", name, n);
        vTaskDelay(pdMS_TO_TICKS(100));// поступлива пауза: контекст (зокрема n) зберігається
    }
}

void setup() {
    Serial.begin(115200);
    static const char a[] = "A", b[] = "B";
    xTaskCreate(taskCounter, "A", 2048, (void *)a, 1, NULL);
    xTaskCreate(taskCounter, "B", 2048, (void *)b, 1, NULL);
}
