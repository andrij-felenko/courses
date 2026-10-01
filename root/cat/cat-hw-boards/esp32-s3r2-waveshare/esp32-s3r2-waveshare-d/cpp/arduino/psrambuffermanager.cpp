#include <Arduino.h>
#include "esp_heap_caps.h"

class PsramBufferManager {
public:
    static uint8_t* createBuffer(size_t bytes) {
        if (!psramFound()) {
            Serial.println("Помилка: PSRAM не виявлено на платі!");
            return nullptr;
        }

        // Виділення пам'яті через нативну функцію ps_malloc
        uint8_t* ptr = (uint8_t*)ps_malloc(bytes);
        if (ptr != nullptr) {
            Serial.printf("Виділено %u байтів у PSRAM. Вільна PSRAM: %u байтів\n", 
                          bytes, ESP.getFreePsram());
        }
        return ptr;
    }
};
