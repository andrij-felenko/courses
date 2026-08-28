#include "driver/gpio.h"
#include "esp_rom_sys.h"                    // esp_rom_delay_us()

#define SERVO_GPIO  GPIO_NUM_18
#define FRAME_US    20000                   // кадр 20 мс = 50 Гц

// кут 0..180°  →  ширина 1000..2000 мкс (лінійна підстановка)
static int angle_to_us(int deg) {
    if (deg < 0)   deg = 0;
    if (deg > 180) deg = 180;
    return 1000 + (int)((long)deg * 1000 / 180);  // 0°→1000, 90°→1500, 180°→2000
}

static void servo_init(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << SERVO_GPIO,       // яку ногу налаштовуємо
        .mode         = GPIO_MODE_OUTPUT,
    };
    gpio_config(&cfg);
}

// один кадр: імпульс заданої ширини + добивання паузи до 20 мс
static void servo_frame(int width_us) {
    gpio_set_level(SERVO_GPIO, 1);
    esp_rom_delay_us(width_us);                   // ширина = кут
    gpio_set_level(SERVO_GPIO, 0);
    esp_rom_delay_us(FRAME_US - width_us);        // решта кадру — пауза
}
