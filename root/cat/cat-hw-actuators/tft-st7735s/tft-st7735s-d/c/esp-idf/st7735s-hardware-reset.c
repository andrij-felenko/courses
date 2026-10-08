#include <stdint.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"

typedef struct {
    uint8_t cmd;
    uint8_t data_len;
    const uint8_t *data;
    uint16_t delay_ms;
} st7735s_init_cmd_t;

static const uint8_t init_colmod[] = { 0x05 }; // 16-bit RGB565
static const uint8_t init_madctl[] = { 0x08 }; // BGR order
static const uint8_t init_frmctr1[] = { 0x01, 0x2C, 0x2D };
static const uint8_t init_pwctr1[]  = { 0xA2, 0x02, 0x84 };
static const uint8_t init_pwctr2[]  = { 0xC5 };
static const uint8_t init_vmctr1[]  = { 0x0E };

static const st7735s_init_cmd_t init_sequence[] = {
    { 0x01, 0, NULL, 120 },                  // SWRESET
    { 0x11, 0, NULL, 120 },                  // SLPOUT
    { 0xB1, 3, init_frmctr1, 0 },            // FRMCTR1
    { 0xC0, 3, init_pwctr1, 0 },             // PWCTR1
    { 0xC1, 1, init_pwctr2, 0 },             // PWCTR2
    { 0xC5, 1, init_vmctr1, 0 },             // VMCTR1
    { 0x36, 1, init_madctl, 0 },             // MADCTL
    { 0x3A, 1, init_colmod, 10 },            // COLMOD
    { 0x29, 0, NULL, 100 }                   // DISPON
};

void st7735s_hardware_reset(gpio_num_t res_pin) {
    gpio_set_level(res_pin, 0);
    vTaskDelay(pdMS_TO_TICKS(10));
    gpio_set_level(res_pin, 1);
    vTaskDelay(pdMS_TO_TICKS(120));
}

void st7735s_init(st7735s_t *dev, gpio_num_t res_pin) {
    st7735s_hardware_reset(res_pin);
    size_t cmd_count = sizeof(init_sequence) / sizeof(init_sequence[0]);
    for (size_t i = 0; i < cmd_count; i++) {
        st7735s_send_cmd(dev, init_sequence[i].cmd);
        if (init_sequence[i].data_len > 0) {
            st7735s_send_data(dev, init_sequence[i].data, init_sequence[i].data_len);
        }
        if (init_sequence[i].delay_ms > 0) {
            vTaskDelay(pdMS_TO_TICKS(init_sequence[i].delay_ms));
        }
    }
}
