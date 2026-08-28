// ESP-IDF: виводи шилда — на вихід, а тик 1 кГц веде дисплей, кнопки й писк
#include "driver/gpio.h"
#include "esp_timer.h"

static void shield_tick(void *arg);   // один розряд, опитування кнопок, відлік писку

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << PIN_LATCH) | (1ULL << PIN_CLK) | (1ULL << PIN_DATA),
        .mode         = GPIO_MODE_OUTPUT,
    };
    ESP_ERROR_CHECK(gpio_config(&io));

    const esp_timer_create_args_t args = { .callback = shield_tick, .name = "mfs" };
    esp_timer_handle_t tim;
    ESP_ERROR_CHECK(esp_timer_create(&args, &tim));
    ESP_ERROR_CHECK(esp_timer_start_periodic(tim, 1000));   // кожні 1000 мкс = 1 кГц
    // з цієї миті дисплей ведеться сам — далі в коді лише логіка
}
