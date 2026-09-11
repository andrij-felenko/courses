/* st7789.c — Реалізація функцій драйвера */
#include "st7789.h"

/* Коди команд контролера ST7789 */
#define CMD_SWRESET 0x01
#define CMD_SLPOUT  0x11
#define CMD_INVON   0x21
#define CMD_DISPON  0x29
#define CMD_CASET   0x2A
#define CMD_RASET   0x2B
#define CMD_RAMWR   0x2C
#define CMD_MADCTL  0x36
#define CMD_COLMOD  0x3A

static void write_cmd(st7789_dev_t *dev, uint8_t cmd)
{
    dev->hal->set_dc(false);  /* Режим передачі команд: DC = 0 */
    dev->hal->set_cs(false);  /* Активація чипа на шині: CS = 0 */
    dev->hal->spi_write(&cmd, 1);
    dev->hal->set_cs(true);   /* Деактивація чипа: CS = 1 */
}

static void write_data(st7789_dev_t *dev, const uint8_t *buf, size_t len)
{
    dev->hal->set_dc(true);   /* Режим передачі даних: DC = 1 */
    dev->hal->set_cs(false);
    dev->hal->spi_write(buf, len);
    dev->hal->set_cs(true);
}

static void write_data_byte(st7789_dev_t *dev, uint8_t data)
{
    write_data(dev, &data, 1);
}

void st7789_init(st7789_dev_t *dev, const st7789_platform_t *hal)
{
    dev->hal = hal;
    /* Зсуви для матриці 240x240 у вікні пам'яті 240x320 */
    dev->offset_x = 0;
    dev->offset_y = 0;

    /* Початковий стан керуючих ліній */
    dev->hal->set_cs(true);
    dev->hal->set_blk(false); /* Підсвічування вимкнено до очищення екрана */

    /* Апаратний імпульс скидання тривалістю 20 мкс */
    dev->hal->set_res(false);
    dev->hal->delay_ms(1);
    dev->hal->set_res(true);
    dev->hal->delay_ms(10);   /* Пауза для зчитування внутрішніх OTP-калібрувань */

    /* Програмне скидання логіки */
    write_cmd(dev, CMD_SWRESET);
    dev->hal->delay_ms(150);

    /* Вихід зі сну та критична пауза заряду помп */
    write_cmd(dev, CMD_SLPOUT);
    dev->hal->delay_ms(120);

    /* Формат пікселя: 16 бітів (RGB565) */
    write_cmd(dev, CMD_COLMOD);
    write_data_byte(dev, 0x55);

    /* Напрямок сканування екрана */
    write_cmd(dev, CMD_MADCTL);
    write_data_byte(dev, 0x00);

    /* Увімкнення інверсії для IPS-матриць */
    write_cmd(dev, CMD_INVON);

    /* Увімкнення розгортки дисплея */
    write_cmd(dev, CMD_DISPON);
    dev->hal->delay_ms(20);

    /* Очищення екрана чорним кольором перед подачею світла */
    st7789_fill_color(dev, 0x0000);

    /* Активація світлодіодного підсвічування */
    dev->hal->set_blk(true);
}

void st7789_set_address_window(st7789_dev_t *dev, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1)
{
    uint16_t x_start = x0 + dev->offset_x;
    uint16_t x_end   = x1 + dev->offset_x;
    uint16_t y_start = y0 + dev->offset_y;
    uint16_t y_end   = y1 + dev->offset_y;

    uint8_t col_buf[4] = {
        (uint8_t)(x_start >> 8), (uint8_t)(x_start & 0xFF),
        (uint8_t)(x_end >> 8),   (uint8_t)(x_end & 0xFF)
    };
    uint8_t row_buf[4] = {
        (uint8_t)(y_start >> 8), (uint8_t)(y_start & 0xFF),
        (uint8_t)(y_end >> 8),   (uint8_t)(y_end & 0xFF)
    };

    write_cmd(dev, CMD_CASET);
    write_data(dev, col_buf, 4);

    write_cmd(dev, CMD_RASET);
    write_data(dev, row_buf, 4);

    /* Переведення контролера в режим запису пікселів */
    write_cmd(dev, CMD_RAMWR);
}

void st7789_fill_color(st7789_dev_t *dev, uint16_t color)
{
    st7789_set_address_window(dev, 0, 0, ST7789_WIDTH - 1, ST7789_HEIGHT - 1);

    /* Підготовка байтів кольору з урахуванням Big-Endian передачі */
    uint8_t pixel[2] = { (uint8_t)(color >> 8), (uint8_t)(color & 0xFF) };

    /* Буфер на 60 пікселів для прискорення блокової передачі */
    uint8_t line_buffer[120];
    for (size_t i = 0; i < 60; ++i) {
        line_buffer[2 * i]     = pixel[0];
        line_buffer[2 * i + 1] = pixel[1];
    }

    dev->hal->set_dc(true);
    dev->hal->set_cs(false);

    size_t total_pixels = ST7789_WIDTH * ST7789_HEIGHT;
    size_t chunks = total_pixels / 60;
    for (size_t i = 0; i < chunks; ++i) {
        dev->hal->spi_write(line_buffer, sizeof(line_buffer));
    }

    dev->hal->set_cs(true);
}

void st7789_draw_pixel(st7789_dev_t *dev, uint16_t x, uint16_t y, uint16_t color)
{
    /* Відсікання координат за межами фізичної матриці */
    if (x >= ST7789_WIDTH || y >= ST7789_HEIGHT) {
        return;
    }

    st7789_set_address_window(dev, x, y, x, y);

    uint8_t pixel[2] = { (uint8_t)(color >> 8), (uint8_t)(color & 0xFF) };
    write_data(dev, pixel, 2);
}

void st7789_fill_rect(st7789_dev_t *dev, uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color)
{
    /* Відсікання прямокутника відносно меж екрана */
    if (x >= ST7789_WIDTH || y >= ST7789_HEIGHT || w == 0 || h == 0) {
        return;
    }
    if (x + w > ST7789_WIDTH) {
        w = ST7789_WIDTH - x;
    }
    if (y + h > ST7789_HEIGHT) {
        h = ST7789_HEIGHT - y;
    }

    st7789_set_address_window(dev, x, y, x + w - 1, y + h - 1);

    uint8_t pixel[2] = { (uint8_t)(color >> 8), (uint8_t)(color & 0xFF) };
    size_t count = (size_t)w * h;

    dev->hal->set_dc(true);
    dev->hal->set_cs(false);
    for (size_t i = 0; i < count; ++i) {
        dev->hal->spi_write(pixel, 2);
    }
    dev->hal->set_cs(true);
}
