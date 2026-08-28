#include "esp_task_wdt.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define WDT_TIMEOUT_MS 5000      // таймаут сторожа, мілісекунди

static void work_task(void *arg) {
    esp_task_wdt_add(NULL);              // стерегти ЦЮ задачу
    for (;;) {
        do_work();                       // якщо завис ТУТ — до годівлі не дійде
        esp_task_wdt_reset();            // дійшли здоровими → скидаємо лічильник
        vTaskDelay(pdMS_TO_TICKS(10));   // віддати час іншим задачам
    }
}

void app_main(void) {
    esp_task_wdt_config_t cfg = {
        .timeout_ms = WDT_TIMEOUT_MS, .idle_core_mask = 0, .trigger_panic = true,
    };
    ESP_ERROR_CHECK(esp_task_wdt_reconfigure(&cfg));  // TWDT уже ввімкнено в menuconfig
    xTaskCreate(work_task, "work", 4096, NULL, 5, NULL);
}
