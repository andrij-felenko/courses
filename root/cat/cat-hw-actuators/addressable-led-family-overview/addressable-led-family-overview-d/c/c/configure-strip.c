// Архітектурна конфігурація вибору чипсета та параметрів шини в C
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    CHIPSET_WS2812B,
    CHIPSET_SK6812_RGBW,
    CHIPSET_APA102,
    CHIPSET_WS2815
} led_chipset_type_t;

typedef struct {
    led_chipset_type_t type;
    uint16_t pixel_count;
    uint8_t color_channels; // 3 для RGB, 4 для RGBW
    bool requires_clock_pin;
    bool has_redundant_data;
    uint32_t max_spi_frequency_hz;
} led_strip_config_t;

led_strip_config_t configure_strip(led_chipset_type_t type, uint16_t count) {
    led_strip_config_t config = {
        .type = type,
        .pixel_count = count,
        .color_channels = (type == CHIPSET_SK6812_RGBW) ? 4 : 3,
        .requires_clock_pin = (type == CHIPSET_APA102),
        .has_redundant_data = (type == CHIPSET_WS2815),
        .max_spi_frequency_hz = (type == CHIPSET_APA102) ? 20000000UL : 800000UL
    };
    return config;
}
