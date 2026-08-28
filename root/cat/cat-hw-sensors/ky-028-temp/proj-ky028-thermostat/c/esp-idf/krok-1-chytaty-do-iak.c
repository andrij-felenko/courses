#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "ky028";
#define DO_PIN  GPIO_NUM_32            // цифровий вихід модуля (поріг компаратора)

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << DO_PIN,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,    // DO вже підтягнутий на платі модуля
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    gpio_config(&cfg);

    while (1) {
        int level = gpio_get_level(DO_PIN);     // 0 або 1 — сирий рівень
        ESP_LOGI(TAG, "%s", level ? "DO = HIGH" : "DO = LOW");
        vTaskDelay(pdMS_TO_TICKS(300));
    }
}
