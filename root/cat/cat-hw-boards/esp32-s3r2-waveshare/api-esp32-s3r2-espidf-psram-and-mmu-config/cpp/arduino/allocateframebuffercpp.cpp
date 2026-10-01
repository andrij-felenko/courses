#include <Arduino.h>
#include "esp_heap_caps.h"

void allocateFrameBufferCPP(size_t width, size_t height) {
    size_t bufferSize = width * height * 2;
    
    // Спроба виділення масиву в PSRAM через C++ API
    uint8_t* frameBuffer = reinterpret_cast<uint8_t*>(
        heap_caps_malloc(bufferSize, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT)
    );
    
    if (frameBuffer == nullptr) {
        Serial.printf("Помилка: Недостатньо PSRAM для %zu байтів\n", bufferSize);
        return;
    }
    
    Serial.printf("Виділено буфер кадру у PSRAM: %p\n", static_cast<void*>(frameBuffer));
    
    // Звільнення буфера
    heap_caps_free(frameBuffer);
}
