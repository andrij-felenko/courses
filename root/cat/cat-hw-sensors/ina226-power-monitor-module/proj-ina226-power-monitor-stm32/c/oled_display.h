#ifndef OLED_DISPLAY_H
#define OLED_DISPLAY_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// I2C-адреса дисплея SSD1306 за замовчуванням
#define OLED_I2C_ADDR_DEFAULT   0x3C

// Геометрія графічного екрана
#define OLED_WIDTH              128
#define OLED_HEIGHT             64
#define OLED_BUFFER_SIZE        ((OLED_WIDTH * OLED_HEIGHT) / 8) // 1024 байти буфера

// Вказівник на функцію запису через I2C для дисплея
typedef bool (*oled_i2c_write_fn)(uint8_t dev_addr, const uint8_t *data, size_t len);

// Дескриптор графічного OLED-дисплея
typedef struct {
    uint8_t           i2c_addr;
    oled_i2c_write_fn i2c_write;
    uint8_t           buffer[OLED_BUFFER_SIZE];
} oled_t;

// Прототипи функцій графічного драйвера OLED
bool oled_init(oled_t *oled, uint8_t i2c_addr, oled_i2c_write_fn write_fn);
void oled_clear(oled_t *oled);
bool oled_update(oled_t *oled);
void oled_draw_pixel(oled_t *oled, int x, int y, bool color);
void oled_draw_char(oled_t *oled, int x, int y, char c, bool color);
void oled_draw_string(oled_t *oled, int x, int y, const char *str, bool color);
void oled_display_measurements(oled_t *oled, uint32_t bus_voltage_mv, int32_t current_ma, uint32_t power_mw, bool alert_active);

#endif // OLED_DISPLAY_H
