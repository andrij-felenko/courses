#include <stdint.h>
#include <string.h>
#include "driver/i2c.h"

#define OLED_I2C_ADDR       0x3C
#define OLED_WIDTH          128
#define OLED_HEIGHT         32
#define OLED_BUFFER_SIZE    (OLED_WIDTH * OLED_HEIGHT / 8)

// Буфер кадрової інформації у локальному ОЗП мікроконтролера
static uint8_t g_framebuffer[OLED_BUFFER_SIZE];

// Установка пікселя за координатами (x, y)
void oled_draw_pixel(int16_t x, int16_t y, uint8_t color) {
    if (x < 0 || x >= OLED_WIDTH || y < 0 || y >= OLED_HEIGHT) {
        return; // Вихід за межі екрана
    }
    
    uint16_t index = x + ((y / 8) * OLED_WIDTH);
    uint8_t bit_mask = 1 << (y % 8);
    
    if (color) {
        g_framebuffer[index] |= bit_mask;  // Засвітити піксель
    } else {
        g_framebuffer[index] &= ~bit_mask; // Погасити піксель
    }
}

// Очищення кадрового буфера
void oled_clear(void) {
    memset(g_framebuffer, 0x00, OLED_BUFFER_SIZE);
}

// Передача кадрового буфера в GDDRAM контролера SSD1306 через I2C
esp_err_t oled_flush(i2c_port_t i2c_num) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OLED_I2C_ADDR << 1) | I2C_MASTER_WRITE, true);
    
    // Префіксний байт 0x40 вказує, що наступні байти є даними для GDDRAM
    i2c_master_write_byte(cmd, 0x40, true);
    i2c_master_write(cmd, g_framebuffer, OLED_BUFFER_SIZE, true);
    i2c_master_stop(cmd);
    
    esp_err_t ret = i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    
    return ret;
}
