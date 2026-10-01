#include <cstdio>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_CPP";

class PsramBuffer {
public:
    uint8_t *data;
    size_t size;

    PsramBuffer(size_t sz) : size(sz) {
        // Виділення пам'яті в PSRAM з вирівнюванням
        data = static_cast<uint8_t*>(heap_caps_malloc(sz, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!data) {
            ESP_LOGE(TAG, "Помилка виділення PSRAM буфера");
        }
    }

    ~PsramBuffer() {
        if (data) {
            heap_caps_free(data);
        }
    }
};

extern "C" void app_main(void)
{
    PsramBuffer buf(100 * 1024);
    if (buf.data) {
        ESP_LOGI(TAG, "C++ об'єкт PSRAM виділено за адресою: %p", buf.data);
    }
}
