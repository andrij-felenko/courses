#include <Arduino.h>
#include "esp_heap_caps.h"

void setup() {
    Serial.begin(115200);
    delay(1000);

    size_t frame_size = 640 * 480 * 2;
    uint8_t *frame_buffer = (uint8_t *)ps_malloc(frame_size);

    if (frame_buffer == nullptr) {
        Serial.println("Помилка виділення пам'яті в PSRAM!");
        return;
    }

    Serial.printf("Буфер успішно виділено в PSRAM: %p\n", frame_buffer);
    Serial.printf("Залишок PSRAM: %u байт\n", ESP.getFreePsram());
    Serial.printf("Залишок SRAM: %u байт\n", ESP.getFreeHeap());

    free(frame_buffer);
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}
