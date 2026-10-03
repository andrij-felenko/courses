#include "mbedtls/platform.h"
#include <Arduino.h>

class MemoryPlatformManager {
public:
    static void* safeCalloc(size_t count, size_t size) {
        size_t total_size = count * size;
        if (ESP.getFreeHeap() < total_size + 8192) {
            // Захист від повного вичерпання купи
            return nullptr;
        }
        return calloc(count, size);
    }

    static void safeFree(void *ptr) {
        if (ptr) free(ptr);
    }

    static void initMemory() {
        mbedtls_platform_set_calloc_free(safeCalloc, safeFree);
    }

    static void feedWatchdog() {
        optimistic_yield(1000);
        yield(); // Скидання WDT у середовищі Arduino ESP8266
    }
};
