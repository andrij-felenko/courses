#include "esp_heap_caps.h"
#include "esp_log.h"
#include <cstddef>

static const char *TAG = "psram_aligned";

void allocate_tensor_buffer() {
    constexpr std::size_t align_bytes = 32;
    constexpr std::size_t tensor_size = 1024 * 512;

    void *tensor_buf = heap_caps_aligned_alloc(align_bytes, tensor_size, MALLOC_CAP_SPIRAM);
    if (tensor_buf == nullptr) {
        ESP_LOGE(TAG, "Помилка виділення вирівняного буфера в PSRAM");
        return;
    }
    ESP_LOGI(TAG, "Тензорний буфер 512 КБ вирівняно по %zu Б за адресою %p", align_bytes, tensor_buf);
    heap_caps_free(tensor_buf);
}
