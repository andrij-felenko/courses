#include "esp_heap_caps.h"

void setup() {
    Serial.begin(115200);

    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    Serial.printf("Доступно PSRAM: %u байтів\n", free_psram);

    // Виділення пам'яті під масив у PSRAM
    uint8_t *buffer = (uint8_t *)heap_caps_malloc(512 * 1024, MALLOC_CAP_SPIRAM);
    if (buffer) {
        Serial.println("Буфер у PSRAM успішно створено");
        heap_caps_free(buffer);
    }
}

void loop() {
}
