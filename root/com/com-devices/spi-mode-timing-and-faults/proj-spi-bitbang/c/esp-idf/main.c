#include "driver/gpio.h"
#include "esp_rom_sys.h"

#define PIN_SCLK GPIO_NUM_18
#define PIN_MOSI GPIO_NUM_23
#define PIN_MISO GPIO_NUM_19
#define PIN_CS   GPIO_NUM_5

void esp_spi_bb_init(uint8_t mode) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_SCLK) | (1ULL << PIN_MOSI) | (1ULL << PIN_CS),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);

    io_conf.pin_bit_mask = (1ULL << PIN_MISO);
    io_conf.mode = GPIO_MODE_INPUT;
    gpio_config(&io_conf);

    gpio_set_level(PIN_CS, 1);
    bool cpol = (mode == 2 || mode == 3);
    gpio_set_level(PIN_SCLK, cpol ? 1 : 0);
}

uint8_t esp_spi_bb_transfer(uint8_t data_out, uint8_t mode) {
    bool cpol = (mode == 2 || mode == 3);
    bool cpha = (mode == 1 || mode == 3);
    uint8_t data_in = 0;

    for (int8_t i = 7; i >= 0; --i) {
        uint32_t bit = (data_out >> i) & 1;

        if (!cpha) {
            gpio_set_level(PIN_MOSI, bit);
            esp_rom_delay_us(1);
            gpio_set_level(PIN_SCLK, !cpol);
            esp_rom_delay_us(1);
            if (gpio_get_level(PIN_MISO)) data_in |= (1 << i);
            gpio_set_level(PIN_SCLK, cpol);
        } else {
            gpio_set_level(PIN_SCLK, !cpol);
            gpio_set_level(PIN_MOSI, bit);
            esp_rom_delay_us(1);
            gpio_set_level(PIN_SCLK, cpol);
            esp_rom_delay_us(1);
            if (gpio_get_level(PIN_MISO)) data_in |= (1 << i);
        }
    }
    return data_in;
}
