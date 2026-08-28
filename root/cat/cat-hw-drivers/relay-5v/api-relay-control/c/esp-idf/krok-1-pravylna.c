// Те саме на ESP-IDF: рівень у засувку виходу СПЕРШУ, драйвер виходу — ПОТІМ.
#include "driver/gpio.h"

#define PIN_RELAY   GPIO_NUM_25   // не завантажувальна ніжка (чому — див. нижче)
#define RELAY_ON    0             // active-low: нуль вмикає
#define RELAY_OFF   1             // одиниця вимикає

void app_main(void) {
    // 1) СПЕРШУ покласти вимкнений рівень у засувку виходу. Ніжка ще не вихід,
    //    тож назовні нічого не йде — рівень просто чекає в регістрі.
    gpio_set_level(PIN_RELAY, RELAY_OFF);

    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_RELAY,
        .mode         = GPIO_MODE_OUTPUT,      // 2) ТІЛЬКИ ТЕПЕР — вихід
        .pull_up_en   = GPIO_PULLUP_ENABLE,    // підтяжка тримає IN у HIGH
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    // Драйвер вмикається вже з рівнем OFF — старт тихий.
}
