#include <stdint.h>
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_NUM_CS   5
#define PIN_NUM_DC   16
#define PIN_NUM_RST  17

static spi_device_handle_t spi_dev;

// Відправка байта команди (лінія DC = 0)
void st7735s_send_cmd(uint8_t cmd) {
    gpio_set_level(PIN_NUM_DC, 0);
    spi_transaction_t t = {
        .length = 8,
        .tx_buffer = &cmd
    };
    spi_device_polling_transmit(spi_dev, &t);
}

// Відправка масиву даних (лінія DC = 1)
void st7735s_send_data(const uint8_t *data, uint16_t len) {
    if (len == 0) return;
    gpio_set_level(PIN_NUM_DC, 1);
    spi_transaction_t t = {
        .length = len * 8,
        .tx_buffer = data
    };
    spi_device_polling_transmit(spi_dev, &t);
}

// Встановлення прямокутного вікна адресації з урахуванням апаратного зсуву
void st7735s_set_window(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1, uint8_t offset_x, uint8_t offset_y) {
    uint8_t caset_data[4] = { 0x00, x0 + offset_x, 0x00, x1 + offset_x };
    uint8_t raset_data[4] = { 0x00, y0 + offset_y, 0x00, y1 + offset_y };

    st7735s_send_cmd(0x2A); // CASET
    st7735s_send_data(caset_data, 4);

    st7735s_send_cmd(0x2B); // RASET
    st7735s_send_data(raset_data, 4);

    st7735s_send_cmd(0x2C); // RAMWR
}
