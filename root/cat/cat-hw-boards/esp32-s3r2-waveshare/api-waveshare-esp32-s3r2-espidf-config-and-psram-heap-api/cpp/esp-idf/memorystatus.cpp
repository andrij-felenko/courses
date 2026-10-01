#include <cstdio>
#include "esp_system.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

constexpr const char *TAG = "SYS_AUDIT_CPP";

struct MemoryStatus {
    size_t free_psram_bytes;
    size_t free_sram_bytes;

    void print_report() const {
        ESP_LOGI(TAG, "Стан ОЗП -> PSRAM: %u байт | SRAM: %u байт", 
                 static_cast<unsigned int>(free_psram_bytes), 
                 static_cast<unsigned int>(free_sram_bytes));
    }
};

MemoryStatus get_current_memory_status() {
    return MemoryStatus{
        heap_caps_get_free_size(MALLOC_CAP_SPIRAM),
        heap_caps_get_free_size(MALLOC_CAP_INTERNAL)
    };
}
