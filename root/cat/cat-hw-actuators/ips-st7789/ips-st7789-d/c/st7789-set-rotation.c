/* Реалізація віконної адресації з урахуванням зсувів та відсікання на C */
#include <stdint.h>
#include <stdbool.h>

#define ST7789_PANEL_WIDTH   240
#define ST7789_PANEL_HEIGHT  240

typedef enum {
    ST7789_ROTATION_0   = 0,
    ST7789_ROTATION_90  = 1,
    ST7789_ROTATION_180 = 2,
    ST7789_ROTATION_270 = 3
} st7789_rotation_t;

static uint16_t x_offset = 0;
static uint16_t y_offset = 0;
static uint16_t current_width = ST7789_PANEL_WIDTH;
static uint16_t current_height = ST7789_PANEL_HEIGHT;

extern void st7789_write_command(uint8_t cmd);
extern void st7789_write_data_byte(uint8_t data);

/* Встановлення кута повороту з розрахунком апаратних зсувів */
void st7789_set_rotation(st7789_rotation_t rot) {
    uint8_t madctl = 0x00;

    switch (rot) {
        case ST7789_ROTATION_0:
            madctl = 0x00; /* MY=0, MX=0, MV=0 */
            x_offset = 0;
            y_offset = 0;
            current_width  = ST7789_PANEL_WIDTH;
            current_height = ST7789_PANEL_HEIGHT;
            break;

        case ST7789_ROTATION_90:
            madctl = 0x60; /* MY=0, MX=1, MV=1 */
            x_offset = 0;
            y_offset = 0;
            current_width  = ST7789_PANEL_HEIGHT;
            current_height = ST7789_PANEL_WIDTH;
            break;

        case ST7789_ROTATION_180:
            madctl = 0xC0; /* MY=1, MX=1, MV=0 */
            x_offset = 0;
            y_offset = 80; /* Компенсація 80 непід'єднаних рядків GRAM */
            current_width  = ST7789_PANEL_WIDTH;
            current_height = ST7789_PANEL_HEIGHT;
            break;

        case ST7789_ROTATION_270:
            madctl = 0xA0; /* MY=1, MX=0, MV=1 */
            x_offset = 80; /* Компенсація 80 непід'єднаних рядків по осі X */
            y_offset = 0;
            current_width  = ST7789_PANEL_HEIGHT;
            current_height = ST7789_PANEL_WIDTH;
            break;
    }

    st7789_write_command(0x36); /* MADCTL */
    st7789_write_data_byte(madctl);
}

/* Відкриття прямокутного вікна оновлення з відсіканням координат */
bool st7789_set_address_window(int16_t x0, int16_t y0, int16_t x1, int16_t y1) {
    /* 1. Повна перевірка виходу за межі екрана */
    if (x0 >= current_width || y0 >= current_height || x1 < 0 || y1 < 0) {
        return false;
    }

    /* 2. Обмеження меж малювання (clipping) */
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 >= current_width)  x1 = current_width - 1;
    if (y1 >= current_height) y1 = current_height - 1;

    /* 3. Додавання апаратних зміщень */
    uint16_t xs = (uint16_t)x0 + x_offset;
    uint16_t xe = (uint16_t)x1 + x_offset;
    uint16_t ys = (uint16_t)y0 + y_offset;
    uint16_t ye = (uint16_t)y1 + y_offset;

    /* 4. Завдання діапазону колонок CASET */
    st7789_write_command(0x2A);
    st7789_write_data_byte((uint8_t)(xs >> 8));
    st7789_write_data_byte((uint8_t)(xs & 0xFF));
    st7789_write_data_byte((uint8_t)(xe >> 8));
    st7789_write_data_byte((uint8_t)(xe & 0xFF));

    /* 5. Завдання діапазону рядків RASET */
    st7789_write_command(0x2B);
    st7789_write_data_byte((uint8_t)(ys >> 8));
    st7789_write_data_byte((uint8_t)(ys & 0xFF));
    st7789_write_data_byte((uint8_t)(ye >> 8));
    st7789_write_data_byte((uint8_t)(ye & 0xFF));

    /* 6. Активація запису в пам'ять RAMWR */
    st7789_write_command(0x2C);

    return true;
}
