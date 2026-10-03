#include <Arduino.h>
#include "lwip/pbuf.h"

class DramHeapManager {
public:
    static struct pbuf* allocateBuffer(uint16_t length) {
        uint32_t freeHeap = ESP.getFreeHeap();
        
        if (freeHeap < 4096) {
            Serial.printf("Недостатньо RAM: %u байт. Скасування.\n", freeHeap);
            return nullptr;
        }

        struct pbuf* p = pbuf_alloc(PBUF_RAW, length, PBUF_RAM);
        if (!p) {
            Serial.println("Помилка pbuf_alloc: фрагментація кучі DRAM!");
        }
        return p;
    }
};
