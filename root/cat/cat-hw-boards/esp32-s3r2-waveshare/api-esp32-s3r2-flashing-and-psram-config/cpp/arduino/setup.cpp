#include <Arduino.h>
#include "esp_heap_caps.h"

void setup() {
    Serial.begin(115200);
    delay(1000);

    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    Serial.printf("Вільна PSRAM: %u байт\n", free_psram);

    size_t buffer_size = 1024 * 1024; // 1 МБ
    uint8_t *buffer = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM);

    if (buffer != nullptr) {
        Serial.printf("Виділено буфер 1 МБ у PSRAM: %p\n", buffer);
        free(buffer);
    } else {
        Serial.println("Помилка виділення у PSRAM!");
    }
}

void loop() {}
