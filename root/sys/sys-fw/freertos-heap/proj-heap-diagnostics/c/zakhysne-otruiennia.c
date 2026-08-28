#include "esp_heap_caps.h"
#include "esp_log.h"

void check_heap_corruption_example(void)
{
    /* Ручна перевірка цілісності всіх зв'язних списків купи */
    bool is_healthy = heap_caps_check_integrity_all(true);

    if (is_healthy) {
        ESP_LOGI("HEAP_CHECK", "Цілісність усіх банків пам'яті підтверджено");
    } else {
        ESP_LOGE("HEAP_CHECK", "ВИЯВЛЕНО ПОШКОДЖЕННЯ КУПИ! Зруйновано канарейки або заголовки");
    }
}
