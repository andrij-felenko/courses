#include "driver/gpio.h"
#include "soc/gpio_struct.h"      // та сама структура GPIO, лише без Arduino

#define PINS ((1u << 2) | (1u << 4) | (1u << 5))   // 0b0011_0100 = 0x34

// 1) напрям: драйвер сам підніме потрібні біти GPIO_ENABLE
gpio_config_t cfg = {
    .pin_bit_mask = (1ULL << 2) | (1ULL << 4) | (1ULL << 5),
    .mode = GPIO_MODE_OUTPUT,
    .pull_up_en = GPIO_PULLUP_DISABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_DISABLE,
};
ESP_ERROR_CHECK(gpio_config(&cfg));   // esp_err_t: помилку не ковтаємо

// 2) перемкнути лише GPIO2 (toggle через OUT)
GPIO.out ^= (1u << 2);            // прямо, ~наносекунди
// для порівняння — те саме обгорткою:
// gpio_set_level(GPIO_NUM_2, !gpio_get_level(GPIO_NUM_2));   // ~мікросекунда

// 3) запалити всі три СИНХРОННО (в одну мить)
GPIO.out_w1ts = PINS;             // 0x34 → GPIO2,4,5 = HIGH однією дією

// 4) погасити ЛИШЕ GPIO4, не торкаючись інших (атомарно)
GPIO.out_w1tc = (1u << 4);        // скинути біт 4 через W1TC
