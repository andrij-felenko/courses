// Реалізація мовою C для типового вбудованого інтерфейсу SPI
#include <stdint.h>
#include <stdbool.h>

// Макроси команд адресації ST7789
#define ST7789_CMD_CASET 0x2A
#define ST7789_CMD_RASET 0x2B

// Прототипи апаратних функцій платформи
void display_spi_write_command(uint8_t cmd);
void display_spi_write_data(const uint8_t *data, uint16_t length);

/**
 * @brief Встановлення прямокутного вікна адресації у пам'яті GRAM
 * @param xs Початковий стовпчик (0..239)
 * @param ys Початковий рядок (0..239)
 * @param xe Кінцевий стовпчик (0..239)
 * @param ye Кінцевий рядок (0..239)
 */
void st7789_set_window(uint16_t xs, uint16_t ys, uint16_t xe, uint16_t ye)
{
    // Буфер для 4 байтів координат стовпчиків: XS[15:8], XS[7:0], XE[15:8], XE[7:0]
    uint8_t col_data[4] = {
        (uint8_t)(xs >> 8),
        (uint8_t)(xs & 0xFF),
        (uint8_t)(xe >> 8),
        (uint8_t)(xe & 0xFF)
    };

    // Буфер для 4 байтів координат рядків: YS[15:8], YS[7:0], YE[15:8], YE[7:0]
    uint8_t row_data[4] = {
        (uint8_t)(ys >> 8),
        (uint8_t)(ys & 0xFF),
        (uint8_t)(ye >> 8),
        (uint8_t)(ye & 0xFF)
    };

    // Встановлення меж стовпчиків (горизонталь)
    display_spi_write_command(ST7789_CMD_CASET);
    display_spi_write_data(col_data, 4);

    // Встановлення меж рядків (вертикаль)
    display_spi_write_command(ST7789_CMD_RASET);
    display_spi_write_data(row_data, 4);
}
