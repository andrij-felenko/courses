#ifndef OLED_H
#define OLED_H

#include <stdint.h>
#include <stdbool.h>

// Геометрія дисплея SSD1306 (128x64 пікселів)
#define OLED_WIDTH   128
#define OLED_HEIGHT  64
#define OLED_BUF_SIZE ((OLED_WIDTH * OLED_HEIGHT) / 8)

// Стан пікселя на монохромній матриці
typedef enum {
    PIXEL_OFF = 0,
    PIXEL_ON  = 1
} oled_pixel_state_t;

// Ініціалізація та керування буфером дисплея
bool oled_init(void);
void oled_clear(void);
void oled_update(void);

// Базові графічні примітиви для побудови тесту
void oled_draw_pixel(uint8_t x, uint8_t y, oled_pixel_state_t state);
void oled_draw_line(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1, oled_pixel_state_t state);
void oled_draw_rect(uint8_t x, uint8_t y, uint8_t w, uint8_t h, oled_pixel_state_t state);

#endif // OLED_H
