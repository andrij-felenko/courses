#include <cstdio>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "HEAP_MONITOR_CPP";

class MemoryChecker {
public:
    static void print_stats() {
        size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
        size_t largest_block = heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM);

        ESP_LOGI(TAG, "[C++] Вільна PSRAM: %zu Б, Макс. блок: %zu Б", free_psram, largest_block);
    }
};
