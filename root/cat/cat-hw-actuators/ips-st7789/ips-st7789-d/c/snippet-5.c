/* st7789.h — Заголовковий файл низькорівневого драйвера */
#ifndef ST7789_H
#define ST7789_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define ST7789_WIDTH   240
#define ST7789_HEIGHT  240

/* Структура інтерфейсу платформи для взаємодії з апаратурою */
typedef struct {
    void (*set_cs)(bool level);
    void (*set_dc)(bool level);
    void (*set_res)(bool level);
    void (*set_blk)(bool level);
    void (*spi_write)(const uint8_t *data, size_t len);
    void (*delay_ms)(uint32_t ms);
} st7789_platform_t;

typedef struct {
    const st7789_platform_t *hal;
    uint16_t offset_x;
    uint16_t offset_y;
} st7789_dev_t;

void st7789_init(st7789_dev_t *dev, const st7789_platform_t *hal);
void st7789_set_address_window(st7789_dev_t *dev, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
void st7789_fill_color(st7789_dev_t *dev, uint16_t color);
void st7789_draw_pixel(st7789_dev_t *dev, uint16_t x, uint16_t y, uint16_t color);
void st7789_fill_rect(st7789_dev_t *dev, uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color);

#endif /* ST7789_H */
