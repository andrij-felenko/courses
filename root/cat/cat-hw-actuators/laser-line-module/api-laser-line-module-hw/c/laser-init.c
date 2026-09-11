#include "driver/gpio.h"
#include "esp_rom_sys.h"

#define LASER_PIN GPIO_NUM_18

void laser_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << LASER_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    gpio_set_level(LASER_PIN, 0); // Безпечний низький рівень при старті
}

void laser_strobe(uint32_t exposure_us) {
    // Відкриваємо транзисторний ключ
    gpio_set_level(LASER_PIN, 1);

    // Затримка на завершення перехідного процесу стабілізатора модуля (50 мкс)
    esp_rom_delay_us(50);

    // Інтервал експозиції камери за стабільної оптичної потужності 5 мВт
    esp_rom_delay_us(exposure_us);

    // Закриваємо ключ
    gpio_set_level(LASER_PIN, 0);
}
