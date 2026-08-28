#include "esp_partition.h"
#include "esp_ota_ops.h"
#include "esp_log.h"

void dump_layout(void) {
    // 1) з якого app-розділу нас запустив завантажувач
    const esp_partition_t *run = esp_ota_get_running_partition();
    ESP_LOGI("part", "виконуюсь із '%s' @ 0x%06lx (%lu КБ)",
             run->label, (unsigned long)run->address,
             (unsigned long)run->size / 1024);

    // 2) знайти розділ NVS за типом+підтипом (label = NULL → перший-ліпший)
    const esp_partition_t *nvs = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_NVS, NULL);
    if (nvs) {
        uint32_t end = nvs->address + nvs->size;          // верхня межа розділу
        ESP_LOGI("part", "nvs @ 0x%06lx..0x%06lx",
                 (unsigned long)nvs->address, (unsigned long)end);
    }
}
