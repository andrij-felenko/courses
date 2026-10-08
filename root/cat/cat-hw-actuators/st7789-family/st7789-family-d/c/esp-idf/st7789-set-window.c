// C (ESP-IDF / Generic C HAL)
#include <stdint.h>
#include <stdbool.h>

#define ST7789_CMD_SLPOUT  0x11
#define ST7789_CMD_INVON   0x21
#define ST7789_CMD_DISPON  0x29
#define ST7789_CMD_CASET   0x2A
#define ST7789_CMD_RASET   0x2B
#define ST7789_CMD_RAMWR   0x2C
#define ST7789_CMD_MADCTL  0x36
#define ST7789_CMD_COLMOD  0x3A

typedef struct {
    uint16_t width;
    uint16_t height;
    uint16_t x_offset;
    uint16_t y_offset;
} st7789_config_t;

void st7789_set_window(const st7789_config_t *cfg, uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2) {
    uint16_t x_start = x1 + cfg->x_offset;
    uint16_t x_end   = x2 + cfg->x_offset;
    uint16_t y_start = y1 + cfg->y_offset;
    uint16_t y_end   = y2 + cfg->y_offset;

    uint8_t caset_data[4] = {
        (uint8_t)(x_start >> 8), (uint8_t)(x_start & 0xFF),
        (uint8_t)(x_end >> 8),   (uint8_t)(x_end & 0xFF)
    };
    uint8_t raset_data[4] = {
        (uint8_t)(y_start >> 8), (uint8_t)(y_start & 0xFF),
        (uint8_t)(y_end >> 8),   (uint8_t)(y_end & 0xFF)
    };

    st7789_write_cmd(ST7789_CMD_CASET);
    st7789_write_data(caset_data, 4);

    st7789_write_cmd(ST7789_CMD_RASET);
    st7789_write_data(raset_data, 4);

    st7789_write_cmd(ST7789_CMD_RAMWR);
}
