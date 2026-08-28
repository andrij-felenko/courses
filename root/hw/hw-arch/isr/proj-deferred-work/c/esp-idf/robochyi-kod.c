#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static volatile bool fired = false;          // спільний прапорець

static void IRAM_ATTR on_event(void *arg) {  // верхня половина: коротка, у RAM
    fired = true;                            // лише відмітити — і вийти
}

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,   // спадний фронт
    };
    gpio_config(&cfg);
    gpio_install_isr_service(ESP_INTR_FLAG_IRAM);
    gpio_isr_handler_add(PIN, on_event, NULL);

    while (1) {                              // нижня половина: тут можна все
        if (fired) {
            fired = false;                   // скинути ПЕРЕД роботою
            ESP_LOGI("app", "подія!");       // друк, обчислення — будь-що
        }
        vTaskDelay(pdMS_TO_TICKS(10));       // віддати CPU іншим задачам
    }
}
