#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "USB_DBG";

void app_main(void)
{
    // Нативний USB Serial/JTAG активний за замовчуванням у ROM
    ESP_LOGI(TAG, "Запуск системи. Нативний USB Serial/JTAG активовано");

    int counter = 0;
    while (1) {
        // Точка зупинки (breakpoint) може бути встановлена на цей рядок у GDB
        counter++;
        ESP_LOGI(TAG, "Ітерація циклу відлагодження: %d", counter);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
