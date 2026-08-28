#include "esp_system.h"

void report_reset_reason(void) {
    esp_reset_reason_t r = esp_reset_reason();
    switch (r) {
        case ESP_RST_BROWNOUT:  puts("reset: BROWNOUT — просіло живлення"); break;
        case ESP_RST_TASK_WDT:  puts("reset: WATCHDOG — зависла задача");    break;
        case ESP_RST_PANIC:     puts("reset: PANIC — аварія в коді");        break;
        case ESP_RST_POWERON:   puts("reset: POWERON — штатний старт");      break;
        default:                printf("reset: інша причина, код %d\n", r);   break;
    }
}
