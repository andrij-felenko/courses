#include "driver/gpio.h"

#define PIN_EN        GPIO_NUM_9    // EN (KEY) модуля
#define PIN_BT_POWER  GPIO_NUM_8    // живлення модуля через транзистор, опційно

void enter_at_mode(void) {
    const gpio_config_t io = {
        .pin_bit_mask = (1ULL << PIN_EN) | (1ULL << PIN_BT_POWER),
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));

    gpio_set_level(PIN_EN, 1);              // EN високо — ЩЕ ДО подачі живлення
    gpio_set_level(PIN_BT_POWER, 0);        // на мить знеструмити…
    vTaskDelay(pdMS_TO_TICKS(100));
    gpio_set_level(PIN_BT_POWER, 1);        // …і подати знову — модуль стартує в AT
    vTaskDelay(pdMS_TO_TICKS(500));         // дати модулю прокинутись
    ESP_ERROR_CHECK(uart_set_baudrate(BT_UART, 38400));  // КОМАНДНА швидкість, не 9600!
}
