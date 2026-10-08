#include <Arduino.h>
#include "esp_psram.h"

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial.println("[PCB INTEGRITY] Запуск фізичного тесту стабільності шини Octal SPI...");

    if (psramFound()) {
        Serial.printf("[PCB INTEGRITY] Octal PSRAM ініціалізовано. Загальний об'єм: %u МБ\n", 
                      ESP.getPsramSize() / (1024 * 1024));

        size_t test_size = 128 * 1024; // 512 КБ
        uint32_t *buf = (uint32_t *)ps_malloc(test_size * sizeof(uint32_t));

        if (buf != nullptr) {
            // Тест на виявлення паразитичних зв'язків між суміжними лініями
            bool pass = true;
            for (size_t i = 0; i < test_size; i++) {
                buf[i] = 0xFF00FF00 ^ i;
            }

            for (size_t i = 0; i < test_size; i++) {
                if (buf[i] != (0xFF00FF00 ^ i)) {
                    pass = false;
                    break;
                }
            }

            free(buf);

            if (pass) {
                Serial.println("[PCB INTEGRITY] Тестування пройдено без помилок! Шина працює стабільно.");
            } else {
                Serial.println("[PCB INTEGRITY] ПОМИЛКА: Виявлено збій читання! Перевірте термінування 22 Ом.");
            }
        }
    } else {
        Serial.println("[PCB INTEGRITY] ПОМИЛКА: PSRAM не виявлено в системі!");
    }
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(10000));
}
