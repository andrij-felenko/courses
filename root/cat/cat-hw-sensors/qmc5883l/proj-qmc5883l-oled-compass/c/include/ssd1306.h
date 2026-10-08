#ifndef SSD1306_H
#define SSD1306_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "i2c_driver.h"

/**
 * @file ssd1306.h
 * @brief Графічний драйвер OLED-дисплея SSD1306 (128x64, I2C).
 */

#define SSD1306_I2C_ADDR_DEFAULT  0x3C
#define SSD1306_WIDTH             128
#define SSD1306_HEIGHT            64
#define SSD1306_BUFFER_SIZE       (SSD1306_WIDTH * SSD1306_HEIGHT / 8)

/* Режими пікселів */
typedef enum {
    SSD1306_COLOR_BLACK = 0, /**< Вимкнений піксель */
    SSD1306_COLOR_WHITE = 1, /**< Увімкнений піксель */
    SSD1306_COLOR_INVERT = 2 /**< Інверсний піксель */
} ssd1306_color_t;

/* Коди помилок SSD1306 */
typedef enum {
    SSD1306_OK       =  0,
    SSD1306_ERR_I2C  = -1,
    SSD1306_ERR_PARAM = -2
} ssd1306_err_t;

/* Контекст дисплея з внутрішнім відеобуфером кадра */
typedef struct {
    uint8_t i2c_addr;
    uint8_t buffer[SSD1306_BUFFER_SIZE];
    bool is_initialized;
} ssd1306_t;

/**
 * @brief Ініціалізація контролера SSD1306 через I2C.
 */
ssd1306_err_t ssd1306_init(ssd1306_t *disp, uint8_t i2c_addr);

/**
 * @brief Очищення буфера кадра (заповнення нулями).
 */
void ssd1306_clear(ssd1306_t *disp);

/**
 * @brief Відправка вмісту внутрішнього буфера кадра на дисплей.
 */
ssd1306_err_t ssd1306_update(ssd1306_t *disp);

/**
 * @brief Малювання одного пікселя у відеобуфері.
 */
void ssd1306_draw_pixel(ssd1306_t *disp, int16_t x, int16_t y, ssd1306_color_t color);

/**
 * @brief Малювання відрізка лінії за алгоритмом Брезенхема.
 */
void ssd1306_draw_line(ssd1306_t *disp, int16_t x0, int16_t y0, int16_t x1, int16_t y1, ssd1306_color_t color);

/**
 * @brief Малювання кола заданого радіуса.
 */
void ssd1306_draw_circle(ssd1306_t *disp, int16_t x0, int16_t y0, int16_t r, ssd1306_color_t color);

/**
 * @brief Малювання заповненого кола.
 */
void ssd1306_draw_filled_circle(ssd1306_t *disp, int16_t x0, int16_t y0, int16_t r, ssd1306_color_t color);

/**
 * @brief Виведення одного символу шрифтом 5x7.
 */
void ssd1306_draw_char(ssd1306_t *disp, int16_t x, int16_t y, char c, ssd1306_color_t color);

/**
 * @brief Виведення текстового рядка на дисплей.
 */
void ssd1306_draw_string(ssd1306_t *disp, int16_t x, int16_t y, const char *str, ssd1306_color_t color);

/**
 * @brief Візуалізація циферблата та векторної стрілки компаса за вказаним азимутом.
 * @param disp Вказівник на екземпляр дисплея.
 * @param cx Центр циферблата X.
 * @param cy Центр циферблата Y.
 * @param radius Радіус кола компаса.
 * @param heading_deg Азимут у градусах (0°..360°).
 */
void ssd1306_draw_compass(ssd1306_t *disp, int16_t cx, int16_t cy, int16_t radius, float heading_deg);

#endif /* SSD1306_H */
