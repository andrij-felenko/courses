#include <cstdio>
#include <cstdlib>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "AUTO_MALLOC_CPP";

void auto_allocation_cpp_demo() {
    // Виклики оператора new перехоплюються стандартним malloc
    uint8_t *large_buffer = new (std::nothrow) uint8_t[65536];

    if (large_buffer) {
        bool in_psram = esp_ptr_external_ram(large_buffer);
        ESP_LOGI(TAG, "Буфер C++ new (64 КБ) у PSRAM: %s", in_psram ? "Так" : "Ні");
        delete[] large_buffer;
    }
}
