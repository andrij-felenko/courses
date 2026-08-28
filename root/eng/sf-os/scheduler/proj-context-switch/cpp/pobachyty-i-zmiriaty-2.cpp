void taskMeasure(void*) {
    Serial.printf("Старт. Вільний стек: %lu слів\n",
                  (uint32_t)uxTaskGetStackHighWaterMark(NULL));

    // Одне перемикання: задача засинає і прокидається
    vTaskDelay(1);   // планувальник збереже кадр регістрів на нашому стеку

    Serial.printf("Після delay. Вільний стек: %lu слів\n",
                  (uint32_t)uxTaskGetStackHighWaterMark(NULL));
    // Різниця — розмір збереженого кадру перемикання
    // (на ESP32/Xtensa: зазвичай 50–80 слів для простої задачі
    //  без апаратного співпроцесора)

    vTaskDelete(NULL);
}

void setup() {
    Serial.begin(115200);
    xTaskCreate(taskMeasure, "meas", 4096, nullptr, 2, nullptr);
}
void loop() { vTaskDelay(portMAX_DELAY); }
