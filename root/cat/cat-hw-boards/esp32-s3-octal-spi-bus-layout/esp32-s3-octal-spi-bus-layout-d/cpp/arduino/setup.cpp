#include <Arduino.h>
#include "esp_psram.h"

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial.println("[OCTAL SPI] Перевірка підсистеми пам'яті ESP32-S3...");

    if (psramFound()) {
        uint32_t total_psram = ESP.getPsramSize();
        uint32_t free_psram = ESP.getFreePsram();
        Serial.printf("[OCTAL SPI] Виявлено PSRAM. Загальний об'єм: %u байт, вільно: %u байт\n", 
                      total_psram, free_psram);

        // Спроба виділення 1 МБ масиву в Octal PSRAM
        uint8_t *psram_array = (uint8_t *)ps_malloc(1024 * 1024);
        if (psram_array != nullptr) {
            Serial.println("[OCTAL SPI] 1 МБ буфер успішно виділено у зовнішній Octal PSRAM");
            free(psram_array);
        } else {
            Serial.println("[OCTAL SPI] Помилка виділення пам'яті ps_malloc!");
        }
    } else {
        Serial.println("[OCTAL SPI] УВАГА: Octal PSRAM не виявлено на шині!");
    }
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}
