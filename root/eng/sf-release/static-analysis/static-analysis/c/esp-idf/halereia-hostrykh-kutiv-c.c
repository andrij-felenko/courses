#include "driver/gpio.h"
#include "esp_log.h"
static const char *TAG = "trap";

// (а) = замість ==
int flag = 0;
if (flag = gpio_get_level(GPIO_NUM_2)) {   // пастка: присвоєння, не порівняння
    ESP_LOGI(TAG, "triggered");            // спрацьовує завжди, коли рівень != 0
}

// (б) звуження типу — маска нульова
uint8_t mask = 1 << 9;                     // 1<<9 = 512 = 0x200; uint8_t → 0
gpio_config_t io = {
    .pin_bit_mask = mask,                  // 0 — жодної ніжки не налаштовано
    .mode = GPIO_MODE_OUTPUT,
};
ESP_ERROR_CHECK(gpio_config(&io));         // мовчки не робить нічого
