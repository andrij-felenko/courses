#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "HEAP_MON";

void heap_monitor_task(void *pvParameters)
{
    (void)pvParameters;

    while (1) {
        size_t free_bytes = xPortGetFreeHeapSize();
        size_t min_ever_free = xPortGetMinimumEverFreeHeapSize();

        ESP_LOGI(TAG, "Поточна вільна RAM: %u Б, історичний мінімум: %u Б",
                 (unsigned int)free_bytes,
                 (unsigned int)min_ever_free);

        /* Якщо історичний мінімум наблизився до небезпечної межі */
        if (min_ever_free < 4096) {
            ESP_LOGW(TAG, "УВАГА: Небезпечне вичерпання купи! Запас < 4 КБ");
        }

        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
