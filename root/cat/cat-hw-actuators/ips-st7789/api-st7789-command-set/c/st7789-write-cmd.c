// Повна реалізація базового драйвера ST7789 мовою C
#include <stdint.h>
#include <stdbool.h>

// Визначення команд
#define CMD_SWRESET 0x01
#define CMD_SLPOUT  0x11
#define CMD_INVON   0x21
#define CMD_DISPON  0x29
#define CMD_CASET   0x2A
#define CMD_RASET   0x2B
#define CMD_RAMWR   0x2C
#define CMD_MADCTL  0x36
#define CMD_COLMOD  0x3A

// Прототипи системних викликів платформи
void hal_gpio_set_reset(bool state);
void hal_gpio_set_dc(bool state);
void hal_gpio_set_cs(bool state);
void hal_gpio_set_backlight(bool state);
void hal_spi_transmit(const uint8_t *data, uint16_t length);
void hal_delay_ms(uint32_t ms);

static uint16_t offset_x = 0;
static uint16_t offset_y = 80;

static void st7789_write_cmd(uint8_t cmd)
{
    hal_gpio_set_dc(false); // Режим команд
    hal_gpio_set_cs(false);
    hal_spi_transmit(&cmd, 1);
    hal_gpio_set_cs(true);
}

static void st7789_write_data_byte(uint8_t data)
{
    hal_gpio_set_dc(true);  // Режим даних
    hal_gpio_set_cs(false);
    hal_spi_transmit(&data, 1);
    hal_gpio_set_cs(true);
}

static void st7789_write_data_buffer(const uint8_t *buffer, uint16_t length)
{
    hal_gpio_set_dc(true);  // Режим даних
    hal_gpio_set_cs(false);
    hal_spi_transmit(buffer, length);
    hal_gpio_set_cs(true);
}

void st7789_set_window(uint16_t xs, uint16_t ys, uint16_t xe, uint16_t ye)
{
    uint16_t adj_xs = xs + offset_x;
    uint16_t adj_xe = xe + offset_x;
    uint16_t adj_ys = ys + offset_y;
    uint16_t adj_ye = ye + offset_y;

    uint8_t col_buf[4] = {
        (uint8_t)(adj_xs >> 8), (uint8_t)(adj_xs & 0xFF),
        (uint8_t)(adj_xe >> 8), (uint8_t)(adj_xe & 0xFF)
    };

    uint8_t row_buf[4] = {
        (uint8_t)(adj_ys >> 8), (uint8_t)(adj_ys & 0xFF),
        (uint8_t)(adj_ye >> 8), (uint8_t)(adj_ye & 0xFF)
    };

    st7789_write_cmd(CMD_CASET);
    st7789_write_data_buffer(col_buf, 4);

    st7789_write_cmd(CMD_RASET);
    st7789_write_data_buffer(row_buf, 4);
}

void st7789_clear(uint16_t color)
{
    st7789_set_window(0, 0, 239, 239);
    st7789_write_cmd(CMD_RAMWR);

    uint8_t color_buf[2] = {
        (uint8_t)(color >> 8),
        (uint8_t)(color & 0xFF)
    };

    hal_gpio_set_dc(true);
    hal_gpio_set_cs(false);
    for (uint32_t i = 0; i < 240 * 240; i++) {
        hal_spi_transmit(color_buf, 2);
    }
    hal_gpio_set_cs(true);
}

/**
 * @brief Повний канонічний цикл ініціалізації контролера ST7789
 */
void st7789_init(void)
{
    // 1. Апаратне скидання
    hal_gpio_set_reset(true);
    hal_delay_ms(10);
    hal_gpio_set_reset(false); // Активний низький рівень
    hal_delay_ms(20);
    hal_gpio_set_reset(true);
    hal_delay_ms(120);

    // 2. Програмне скидання
    st7789_write_cmd(CMD_SWRESET);
    hal_delay_ms(120);

    // 3. Вихід зі сну
    st7789_write_cmd(CMD_SLPOUT);
    hal_delay_ms(120);

    // 4. Формат пікселів: 16-бітний RGB565
    st7789_write_cmd(CMD_COLMOD);
    st7789_write_data_byte(0x55);

    // 5. Орієнтація екрана за замовчуванням
    st7789_write_cmd(CMD_MADCTL);
    st7789_write_data_byte(0x00);

    // 6. Увімкнення інверсії (критично для матриць IPS)
    st7789_write_cmd(CMD_INVON);

    // 7. Попереднє очищення пам'яті чорним кольором перед активацією розгортки
    st7789_clear(0x0000);

    // 8. Увімкнення показу
    st7789_write_cmd(CMD_DISPON);
    hal_delay_ms(20);

    // 9. Активація підсвічування дисплея
    hal_gpio_set_backlight(true);
}
