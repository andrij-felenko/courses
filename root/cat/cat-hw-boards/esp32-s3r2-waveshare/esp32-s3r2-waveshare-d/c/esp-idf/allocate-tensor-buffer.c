#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "psram_aligned";

void allocate_tensor_buffer(void) {
    size_t align_bytes = 32; // Вирівнювання за розміром кеш-лінії L1 (32 байти)
    size_t tensor_size = 1024 * 512; // 512 КБ для тензора моделі Edge AI

    void *tensor_buf = heap_caps_aligned_alloc(align_bytes, tensor_size, MALLOC_CAP_SPIRAM);
    if (tensor_buf == NULL) {
        ESP_LOGE(TAG, "Помилка виділення вирівняного буфера в PSRAM");
        return;
    }
    ESP_LOGI(TAG, "Тензорний буфер 512 КБ вирівняно по %d Б за адресою %p", align_bytes, tensor_buf);
    heap_caps_free(tensor_buf);
}
