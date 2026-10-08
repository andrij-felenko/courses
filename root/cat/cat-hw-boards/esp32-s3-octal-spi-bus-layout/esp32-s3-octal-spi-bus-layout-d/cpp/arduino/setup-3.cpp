#include <Arduino.h>
#include "esp_system.h"

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial.println("[OCTAL BUS] Тестування стабільності пропускної здатності шини...");

    if (psramFound()) {
        size_t test_size = 512 * 1024; // 512 КБ
        uint8_t *ptr = (uint8_t *)ps_malloc(test_size);

        if (ptr != nullptr) {
            uint32_t t0 = millis();
            memset(ptr, 0xEE, test_size);
            uint32_t t_write = millis() - t0;

            Serial.printf("[OCTAL BUS] Запис %u байт виконано за %u мс\n", test_size, t_write);
            free(ptr);
        } else {
            Serial.println("[OCTAL BUS] Помилка: ps_malloc повернув NULL!");
        }
    } else {
        Serial.println("[OCTAL BUS] Помилка: PSRAM не підключена!");
    }
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(5000));
}
