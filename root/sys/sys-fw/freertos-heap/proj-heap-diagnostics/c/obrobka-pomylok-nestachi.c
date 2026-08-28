#include "esp_heap_caps.h"
#include "esp_log.h"

static void on_allocation_failure(size_t size, uint32_t caps, const char *function_name)
{
    ESP_LOGE("HEAP_FAIL", "Відхилено запит на %u байтів у функції %s (можливості: 0x%08x)",
             (unsigned int)size,
             function_name ? function_name : "UNKNOWN",
             (unsigned int)caps);

    if (caps & MALLOC_CAP_DMA) {
        ESP_LOGE("HEAP_FAIL", "Критичний збій: вичерпано внутрішню пам'ять DMA!");
    } else if (caps & MALLOC_CAP_SPIRAM) {
        ESP_LOGE("HEAP_FAIL", "Вичерпано зовнішню пам'ять PSRAM!");
    }
}

void register_heap_fail_handler(void)
{
    esp_err_t err = heap_caps_register_failed_alloc_callback(on_allocation_failure);
    if (err == ESP_OK) {
        ESP_LOGI("HEAP_FAIL", "Обробник збоїв алокації успішно зареєстровано");
    }
}
