// Реалізація мовою C
#include <stdint.h>
#include <stddef.h>

#define ST7789_CMD_RAMWR 0x2C

void display_spi_write_command(uint8_t cmd);
void display_spi_write_data(const uint8_t *data, uint16_t length);
void st7789_set_window(uint16_t xs, uint16_t ys, uint16_t xe, uint16_t ye);

/**
 * @brief Заповнення прямокутної області екрана одним кольором
 * @param x Початкова координата X
 * @param y Початкова координата Y
 * @param w Ширина прямокутника
 * @param h Висота прямокутника
 * @param color 16-бітний колір RGB565
 */
void st7789_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color)
{
    if (w == 0 || h == 0) return;

    // 1. Фіксуємо межі вікна
    st7789_set_window(x, y, x + w - 1, y + h - 1);

    // 2. Активуємо потоковий запис у відеопам'ять
    display_spi_write_command(ST7789_CMD_RAMWR);

    // 3. Готуємо байти кольору у порядку Big-Endian (MSB першим)
    uint8_t color_bytes[2] = {
        (uint8_t)(color >> 8),
        (uint8_t)(color & 0xFF)
    };

    // 4. Передаємо потік пікселів
    uint32_t total_pixels = (uint32_t)w * h;
    for (uint32_t i = 0; i < total_pixels; i++) {
        display_spi_write_data(color_bytes, 2);
    }
}

/**
 * @brief Вивантаження готового масиву пікселів у вікно екрана
 * @param x Початкова координата X
 * @param y Початкова координата Y
 * @param w Ширина області
 * @param h Висота області
 * @param pixels Масив 16-бітних пікселів RGB565
 */
void st7789_draw_image(uint16_t x, uint16_t y, uint16_t w, uint16_t h, const uint16_t *pixels)
{
    if (w == 0 || h == 0 || pixels == NULL) return;

    st7789_set_window(x, y, x + w - 1, y + h - 1);
    display_spi_write_command(ST7789_CMD_RAMWR);

    uint32_t total_pixels = (uint32_t)w * h;
    for (uint32_t i = 0; i < total_pixels; i++) {
        uint16_t c = pixels[i];
        uint8_t color_bytes[2] = {
            (uint8_t)(c >> 8),
            (uint8_t)(c & 0xFF)
        };
        display_spi_write_data(color_bytes, 2);
    }
}
