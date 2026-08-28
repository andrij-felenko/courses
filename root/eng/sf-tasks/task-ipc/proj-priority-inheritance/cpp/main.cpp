// ESP32 / Arduino-FreeRTOS
// Перемкніть один рядок у setup(), щоб побачити різницю в поведінці:
//   lock = xSemaphoreCreateBinary(); xSemaphoreGive(lock);   // ✗ інверсія
//   lock = xSemaphoreCreateMutex();                           // ✓ успадкування

#include <Arduino.h>

SemaphoreHandle_t lock;

// Низька Н (prio 1): бере замок, «довго» в критичній секції (~5 мс)
void lowTask(void*) {
    for (;;) {
        xSemaphoreTake(lock, portMAX_DELAY);
        // --- критична секція (моделюємо роботу з ресурсом) ---
        uint32_t end = millis() + 5;
        while (millis() < end) { /* busy-work */ }
        xSemaphoreGive(lock);
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// Середня С (prio 2): молотить CPU без замка — моделює «іншу роботу»
void midTask(void*) {
    for (;;) {
        volatile uint32_t x = 0;
        for (uint32_t i = 0; i < 200000; ++i) x += i; // ~2–4 мс
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// Висока В (prio 3): заміряє, скільки чекала замку
void highTask(void*) {
    for (;;) {
        uint32_t t0 = millis();
        xSemaphoreTake(lock, portMAX_DELAY);   // <-- скільки чекали?
        uint32_t waited = millis() - t0;
        xSemaphoreGive(lock);
        Serial.printf("В чекала %lu мс\n", waited);
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}

void setup() {
    Serial.begin(115200);

    // ✗ Бінарний семафор — НЕМАЄ успадкування → інверсія:
    lock = xSemaphoreCreateBinary();
    xSemaphoreGive(lock);

    // ✓ М'ютекс — Є успадкування → інверсії немає (розкоментуйте):
    // lock = xSemaphoreCreateMutex();

    // Всі на одному ядрі — щоб витіснення було чітко видиме
    xTaskCreatePinnedToCore(lowTask,  "Low",  2048, NULL, 1, NULL, 1);
    xTaskCreatePinnedToCore(midTask,  "Mid",  2048, NULL, 2, NULL, 1);
    xTaskCreatePinnedToCore(highTask, "High", 2048, NULL, 3, NULL, 1);
}

void loop() { vTaskDelay(pdMS_TO_TICKS(1000)); }
