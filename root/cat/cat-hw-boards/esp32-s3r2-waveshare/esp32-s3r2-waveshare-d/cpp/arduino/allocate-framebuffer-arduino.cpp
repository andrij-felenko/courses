// Виділення кадрового буфера в PSRAM у середовищі Arduino IDE
#include <Arduino.h>

void allocate_framebuffer_arduino(size_t fb_size) {
    if (!psramFound()) {
        Serial.println("PSRAM не виявлено!");
        return;
    }
    uint8_t *fb = (uint8_t *)ps_malloc(fb_size);
    if (fb == NULL) {
        Serial.println("Не вдалося виділити пам'ять у PSRAM!");
        return;
    }
    Serial.printf("Успішно виділено %d байт у PSRAM\n", fb_size);
    // Робота з буфером...
    free(fb);
}
