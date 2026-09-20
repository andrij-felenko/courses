#include "driver/gpio.h"
#include "esp_log.h"
#include <stdint.h>

#define DIP_PIN_BIT0  GPIO_NUM_4
#define DIP_PIN_BIT1  GPIO_NUM_5
#define DIP_PIN_BIT2  GPIO_NUM_6
#define DIP_PIN_BIT3  GPIO_NUM_7

typedef struct {
    uint8_t device_address; // Біти 0..1 (значення 0..3)
    bool high_speed_mode;   // Біт 2
    bool parity_enable;     // Біт 3
} dip_config_t;

dip_config_t dip_switch_read(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << DIP_PIN_BIT0) | (1ULL << DIP_PIN_BIT1) |
                        (1ULL << DIP_PIN_BIT2) | (1ULL << DIP_PIN_BIT3),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    // Сире зчитування 4 пінів (0 = замкнено/ON, 1 = розімкнено/OFF)
    uint8_t raw = 0;
    raw |= (gpio_get_level(DIP_PIN_BIT0) << 0);
    raw |= (gpio_get_level(DIP_PIN_BIT1) << 1);
    raw |= (gpio_get_level(DIP_PIN_BIT2) << 2);
    raw |= (gpio_get_level(DIP_PIN_BIT3) << 3);

    // Інвертування 4-бітного значення для прямої логіки
    uint8_t direct = (~raw) & 0x0F;

    dip_config_t config;
    config.device_address = (direct & 0x03) >> 0;
    config.high_speed_mode = (direct & 0x04) >> 2;
    config.parity_enable    = (direct & 0x08) >> 3;

    return config;
}
