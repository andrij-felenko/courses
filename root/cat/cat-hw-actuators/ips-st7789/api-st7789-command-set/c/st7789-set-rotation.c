// Реалізація мовою C
#include <stdint.h>

#define ST7789_CMD_MADCTL 0x36
#define ST7789_CMD_CASET  0x2A
#define ST7789_CMD_RASET  0x2B

// Бітові маски регістра MADCTL
#define MADCTL_MY  0x80  // Дзеркалювання рядків (Row Address Order)
#define MADCTL_MX  0x40  // Дзеркалювання стовпчиків (Column Address Order)
#define MADCTL_MV  0x20  // Обмін осей X/Y (Row/Column Exchange)
#define MADCTL_BGR 0x08  // Вибір порядку субпікселів BGR замість RGB

static uint16_t display_offset_x = 0;
static uint16_t display_offset_y = 0;

void display_spi_write_command(uint8_t cmd);
void display_spi_write_data(const uint8_t *data, uint16_t length);

/**
 * @brief Встановлення орієнтації екрана з корекцією апаратних зсувів 240x240
 * @param rotation Кут повороту (0: 0°, 1: 90°, 2: 180°, 3: 270°)
 */
void st7789_set_rotation(uint8_t rotation)
{
    uint8_t madctl_val = 0;

    switch (rotation & 0x03) {
        case 0: // Портретна 0°
            madctl_val = 0x00;
            display_offset_x = 0;
            display_offset_y = 80; // Зсув за рядками
            break;

        case 1: // Ландшафтна 90°
            madctl_val = MADCTL_MX | MADCTL_MV;
            display_offset_x = 80; // Зсув перейшов на вісь стовпчиків
            display_offset_y = 0;
            break;

        case 2: // Портретна 180°
            madctl_val = MADCTL_MX | MADCTL_MY;
            display_offset_x = 0;
            display_offset_y = 0;
            break;

        case 3: // Ландшафтна 270°
            madctl_val = MADCTL_MY | MADCTL_MV;
            display_offset_x = 0;
            display_offset_y = 0;
            break;
    }

    display_spi_write_command(ST7789_CMD_MADCTL);
    display_spi_write_data(&madctl_val, 1);
}

/**
 * @brief Кориговане встановлення вікна адресації з урахуванням зміщень GRAM
 */
void st7789_set_window_corrected(uint16_t xs, uint16_t ys, uint16_t xe, uint16_t ye)
{
    // Додаємо апаратний зсув до логічних координат
    uint16_t adj_xs = xs + display_offset_x;
    uint16_t adj_xe = xe + display_offset_x;
    uint16_t adj_ys = ys + display_offset_y;
    uint16_t adj_ye = ye + display_offset_y;

    uint8_t col_data[4] = {
        (uint8_t)(adj_xs >> 8), (uint8_t)(adj_xs & 0xFF),
        (uint8_t)(adj_xe >> 8), (uint8_t)(adj_xe & 0xFF)
    };

    uint8_t row_data[4] = {
        (uint8_t)(adj_ys >> 8), (uint8_t)(adj_ys & 0xFF),
        (uint8_t)(adj_ye >> 8), (uint8_t)(adj_ye & 0xFF)
    };

    display_spi_write_command(ST7789_CMD_CASET);
    display_spi_write_data(col_data, 4);

    display_spi_write_command(ST7789_CMD_RASET);
    display_spi_write_data(row_data, 4);
}
