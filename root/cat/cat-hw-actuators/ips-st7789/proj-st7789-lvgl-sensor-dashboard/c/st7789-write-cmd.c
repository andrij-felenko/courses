#include <stdint.h>
#include <stddef.h>

/* Команди контролера ST7789 */
#define ST7789_SWRESET 0x01
#define ST7789_SLPOUT  0x11
#define ST7789_INVON   0x21
#define ST7789_DISPON  0x29
#define ST7789_CASET   0x2A
#define ST7789_RASET   0x2B
#define ST7789_RAMWR   0x2C
#define ST7789_MADCTL  0x36
#define ST7789_COLMOD  0x3A

/* Апаратне зміщення для модуля 1.3" 240x240 */
#define ST7789_X_OFFSET 0
#define ST7789_Y_OFFSET 20
#define ST7789_WIDTH    240
#define ST7789_HEIGHT   240

/* Апаратно-залежні прототипи керування лініями (реалізуються для конкретного МК) */
void hal_gpio_write_cs(uint8_t level);
void hal_gpio_write_dc(uint8_t level);
void hal_gpio_write_res(uint8_t level);
void hal_spi_transmit(const uint8_t *data, size_t length);
void hal_delay_ms(uint32_t ms);

/* Відправка байта команди */
static void st7789_write_cmd(uint8_t cmd)
{
    hal_gpio_write_dc(0); /* Режим команди */
    hal_gpio_write_cs(0); /* Активація дисплея */
    hal_spi_transmit(&cmd, 1);
    hal_gpio_write_cs(1);
}

/* Відправка масиву даних */
static void st7789_write_data(const uint8_t *data, size_t length)
{
    hal_gpio_write_dc(1); /* Режим даних */
    hal_gpio_write_cs(0);
    hal_spi_transmit(data, length);
    hal_gpio_write_cs(1);
}

/* Встановлення адреси активного вікна з урахуванням зсувів */
void st7789_set_window(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
    uint8_t cols[4];
    uint8_t rows[4];

    /* Додавання апаратного зміщення матриці */
    x1 += ST7789_X_OFFSET;
    x2 += ST7789_X_OFFSET;
    y1 += ST7789_Y_OFFSET;
    y2 += ST7789_Y_OFFSET;

    cols[0] = (uint8_t)(x1 >> 8);
    cols[1] = (uint8_t)(x1 & 0xFF);
    cols[2] = (uint8_t)(x2 >> 8);
    cols[3] = (uint8_t)(x2 & 0xFF);

    rows[0] = (uint8_t)(y1 >> 8);
    rows[1] = (uint8_t)(y1 & 0xFF);
    rows[2] = (uint8_t)(y2 >> 8);
    rows[3] = (uint8_t)(y2 & 0xFF);

    st7789_write_cmd(ST7789_CASET);
    st7789_write_data(cols, 4);

    st7789_write_cmd(ST7789_RASET);
    st7789_write_data(rows, 4);

    st7789_write_cmd(ST7789_RAMWR);
}

/* Повна апаратна ініціалізація модуля */
void st7789_init(void)
{
    uint8_t colmod_param = 0x55; /* RGB565 16-біт колір */
    uint8_t madctl_param = 0x00; /* Стандартна орієнтація */

    /* Апаратний імпульс скидання */
    hal_gpio_write_res(0);
    hal_delay_ms(20);
    hal_gpio_write_res(1);
    hal_delay_ms(150);

    /* Програмне скидання та вихід зі сну */
    st7789_write_cmd(ST7789_SWRESET);
    hal_delay_ms(150);

    st7789_write_cmd(ST7789_SLPOUT);
    hal_delay_ms(150);

    /* Формат пікселя */
    st7789_write_cmd(ST7789_COLMOD);
    st7789_write_data(&colmod_param, 1);

    /* Напрямок пам'яті */
    st7789_write_cmd(ST7789_MADCTL);
    st7789_write_data(&madctl_param, 1);

    /* Інверсія для панелей IPS */
    st7789_write_cmd(ST7789_INVON);
    hal_delay_ms(10);

    /* Увімкнення виходу на екран */
    st7789_write_cmd(ST7789_DISPON);
    hal_delay_ms(20);
}
