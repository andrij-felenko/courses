#include <stdint.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"

#define ST7735S_CMD_CASET  0x2A
#define ST7735S_CMD_RASET  0x2B
#define ST7735S_CMD_RAMWR  0x2C
#define ST7735S_CMD_MADCTL 0x36

#define ST7735S_MADCTL_MY  0x80
#define ST7735S_MADCTL_MX  0x40
#define ST7735S_MADCTL_MV  0x20
#define ST7735S_MADCTL_BGR 0x08

typedef struct {
    spi_device_handle_t spi_dev;
    gpio_num_t dc_pin;
    uint8_t offset_x;
    uint8_t offset_y;
} st7735s_t;

static void st7735s_send_cmd(st7735s_t *dev, uint8_t cmd) {
    gpio_set_level(dev->dc_pin, 0);
    spi_transaction_t t = {
        .length = 8,
        .tx_buffer = &cmd
    };
    spi_device_polling_transmit(dev->spi_dev, &t);
}

static void st7735s_send_data(st7735s_t *dev, const uint8_t *data, size_t len) {
    if (len == 0) return;
    gpio_set_level(dev->dc_pin, 1);
    spi_transaction_t t = {
        .length = len * 8,
        .tx_buffer = data
    };
    spi_device_polling_transmit(dev->spi_dev, &t);
}

void st7735s_set_window(st7735s_t *dev, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    uint16_t xs = x0 + dev->offset_x;
    uint16_t xe = x1 + dev->offset_x;
    uint16_t ys = y0 + dev->offset_y;
    uint16_t ye = y1 + dev->offset_y;

    uint8_t caset_data[4] = { xs >> 8, xs & 0xFF, xe >> 8, xe & 0xFF };
    st7735s_send_cmd(dev, ST7735S_CMD_CASET);
    st7735s_send_data(dev, caset_data, 4);

    uint8_t raset_data[4] = { ys >> 8, ys & 0xFF, ye >> 8, ye & 0xFF };
    st7735s_send_cmd(dev, ST7735S_CMD_RASET);
    st7735s_send_data(dev, raset_data, 4);

    st7735s_send_cmd(dev, ST7735S_CMD_RAMWR);
}

void st7735s_set_orientation(st7735s_t *dev, uint8_t rotation) {
    uint8_t madctl = ST7735S_MADCTL_BGR;
    switch (rotation & 3) {
        case 0: // Portrait 0°
            madctl |= 0;
            break;
        case 1: // Landscape 90°
            madctl |= (ST7735S_MADCTL_MX | ST7735S_MADCTL_MV);
            break;
        case 2: // Inverted Portrait 180°
            madctl |= (ST7735S_MADCTL_MY | ST7735S_MADCTL_MX);
            break;
        case 3: // Inverted Landscape 270°
            madctl |= (ST7735S_MADCTL_MY | ST7735S_MADCTL_MV);
            break;
    }
    st7735s_send_cmd(dev, ST7735S_CMD_MADCTL);
    st7735s_send_data(dev, &madctl, 1);
}
