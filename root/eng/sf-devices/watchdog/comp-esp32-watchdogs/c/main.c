#include "esp_task_wdt.h"

void app_main(void) {
    esp_task_wdt_config_t wdt = {
        .timeout_ms     = 5000,                   // 5 с на оберт
        .idle_core_mask = (1 << 0) | (1 << 1),   // обидва idle
        .trigger_panic  = true,                   // протух → паніка + reset
    };
    esp_task_wdt_init(&wdt);      // або reconfigure, якщо вже live
    esp_task_wdt_add(NULL);       // стерегти ЦЮ задачу

    for (;;) {
        do_work();                // завис тут — до reset не дійде
        esp_task_wdt_reset();     // доказ поступу → годуємо
    }
}
