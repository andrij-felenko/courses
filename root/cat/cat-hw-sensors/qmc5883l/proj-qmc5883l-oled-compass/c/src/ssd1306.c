#include "ssd1306.h"
#include <string.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

/**
 * @file ssd1306.c
 * @brief Реалізація графичного драйвера та примітивів виведення на OLED SSD1306.
 */

/* Таблиця растрового шрифту 5x7 для ASCII символів (0x20 - 0x7E) */
static const uint8_t font5x7[][5] = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, /* Space */
    {0x00, 0x00, 0x5F, 0x00, 0x00}, /* ! */
    {0x00, 0x07, 0x00, 0x07, 0x00}, /* " */
    {0x14, 0x7F, 0x14, 0x7F, 0x14}, /* # */
    {0x24, 0x2A, 0x7F, 0x2A, 0x12}, /* $ */
    {0x23, 0x13, 0x08, 0x64, 0x62}, /* % */
    {0x36, 0x49, 0x55, 0x22, 0x50}, /* & */
    {0x00, 0x05, 0x03, 0x00, 0x00}, /* ' */
    {0x00, 0x1C, 0x22, 0x41, 0x00}, /* ( */
    {0x00, 0x41, 0x22, 0x1C, 0x00}, /* ) */
    {0x14, 0x08, 0x3E, 0x08, 0x14}, /* * */
    {0x08, 0x08, 0x3E, 0x08, 0x08}, /* + */
    {0x00, 0x50, 0x30, 0x00, 0x00}, /* , */
    {0x08, 0x08, 0x08, 0x08, 0x08}, /* - */
    {0x00, 0x60, 0x60, 0x00, 0x00}, /* . */
    {0x20, 0x10, 0x08, 0x04, 0x02}, /* / */
    {0x3E, 0x51, 0x49, 0x45, 0x3E}, /* 0 */
    {0x00, 0x42, 0x7F, 0x40, 0x00}, /* 1 */
    {0x42, 0x61, 0x51, 0x49, 0x46}, /* 2 */
    {0x21, 0x41, 0x45, 0x4B, 0x31}, /* 3 */
    {0x18, 0x14, 0x12, 0x7F, 0x10}, /* 4 */
    {0x27, 0x45, 0x45, 0x45, 0x39}, /* 5 */
    {0x3C, 0x4A, 0x49, 0x49, 0x30}, /* 6 */
    {0x01, 0x71, 0x09, 0x05, 0x03}, /* 7 */
    {0x36, 0x49, 0x49, 0x49, 0x36}, /* 8 */
    {0x06, 0x49, 0x49, 0x29, 0x1E}, /* 9 */
    {0x00, 0x36, 0x36, 0x00, 0x00}, /* : */
    {0x00, 0x56, 0x36, 0x00, 0x00}, /* ; */
    {0x08, 0x14, 0x22, 0x41, 0x00}, /* < */
    {0x14, 0x14, 0x14, 0x14, 0x14}, /* = */
    {0x00, 0x41, 0x22, 0x14, 0x08}, /* > */
    {0x02, 0x01, 0x51, 0x09, 0x06}, /* ? */
    {0x32, 0x49, 0x79, 0x41, 0x3E}, /* @ */
    {0x7E, 0x11, 0x11, 0x11, 0x7E}, /* A */
    {0x7F, 0x49, 0x49, 0x49, 0x36}, /* B */
    {0x3E, 0x41, 0x41, 0x41, 0x22}, /* C */
    {0x7F, 0x41, 0x41, 0x22, 0x1C}, /* D */
    {0x7F, 0x49, 0x49, 0x49, 0x41}, /* E */
    {0x7F, 0x09, 0x09, 0x09, 0x06}, /* F */
    {0x3E, 0x41, 0x49, 0x49, 0x7A}, /* G */
    {0x7F, 0x08, 0x08, 0x08, 0x7F}, /* H */
    {0x00, 0x41, 0x7F, 0x41, 0x00}, /* I */
    {0x20, 0x40, 0x41, 0x3F, 0x01}, /* J */
    {0x7F, 0x08, 0x14, 0x22, 0x41}, /* K */
    {0x7F, 0x40, 0x40, 0x40, 0x40}, /* L */
    {0x7F, 0x02, 0x0C, 0x02, 0x7F}, /* M */
    {0x7F, 0x04, 0x08, 0x10, 0x7F}, /* N */
    {0x3E, 0x41, 0x41, 0x41, 0x3E}, /* O */
    {0x7F, 0x09, 0x09, 0x09, 0x06}, /* P */
    {0x3E, 0x41, 0x51, 0x21, 0x5E}, /* Q */
    {0x7F, 0x09, 0x19, 0x29, 0x46}, /* R */
    {0x46, 0x49, 0x49, 0x49, 0x31}, /* S */
    {0x01, 0x01, 0x7F, 0x01, 0x01}, /* T */
    {0x3F, 0x40, 0x40, 0x40, 0x3F}, /* U */
    {0x1F, 0x20, 0x40, 0x20, 0x1F}, /* V */
    {0x3F, 0x40, 0x38, 0x40, 0x3F}, /* W */
    {0x63, 0x14, 0x08, 0x14, 0x63}, /* X */
    {0x07, 0x08, 0x70, 0x08, 0x07}, /* Y */
    {0x61, 0x51, 0x49, 0x45, 0x43}, /* Z */
    {0x00, 0x7F, 0x41, 0x41, 0x00}, /* [ */
    {0x02, 0x04, 0x08, 0x10, 0x20}, /* \ */
    {0x00, 0x41, 0x41, 0x7F, 0x00}, /* ] */
    {0x04, 0x02, 0x01, 0x02, 0x04}, /* ^ */
    {0x40, 0x40, 0x40, 0x40, 0x40}, /* _ */
    {0x00, 0x01, 0x02, 0x04, 0x00}, /* ` */
    {0x20, 0x54, 0x54, 0x54, 0x78}, /* a */
    {0x7F, 0x48, 0x44, 0x44, 0x38}, /* b */
    {0x38, 0x44, 0x44, 0x44, 0x20}, /* c */
    {0x38, 0x44, 0x44, 0x48, 0x7F}, /* d */
    {0x38, 0x54, 0x54, 0x54, 0x18}, /* e */
    {0x08, 0x7E, 0x09, 0x01, 0x02}, /* f */
    {0x0C, 0x52, 0x52, 0x52, 0x3E}, /* g */
    {0x7F, 0x08, 0x04, 0x04, 0x78}, /* h */
    {0x00, 0x44, 0x7D, 0x40, 0x00}, /* i */
    {0x20, 0x40, 0x44, 0x3D, 0x00}, /* j */
    {0x7F, 0x10, 0x28, 0x44, 0x00}, /* k */
    {0x00, 0x41, 0x7F, 0x40, 0x00}, /* l */
    {0x7C, 0x04, 0x18, 0x04, 0x78}, /* m */
    {0x7C, 0x08, 0x04, 0x04, 0x78}, /* n */
    {0x38, 0x44, 0x44, 0x44, 0x38}, /* o */
    {0x7C, 0x14, 0x14, 0x14, 0x08}, /* p */
    {0x08, 0x14, 0x14, 0x18, 0x7C}, /* q */
    {0x7C, 0x08, 0x04, 0x04, 0x08}, /* r */
    {0x48, 0x54, 0x54, 0x54, 0x20}, /* s */
    {0x04, 0x3E, 0x44, 0x40, 0x20}, /* t */
    {0x3C, 0x40, 0x40, 0x20, 0x7C}, /* u */
    {0x1C, 0x20, 0x40, 0x20, 0x1C}, /* v */
    {0x3C, 0x40, 0x30, 0x40, 0x3C}, /* w */
    {0x44, 0x28, 0x10, 0x28, 0x44}, /* x */
    {0x0C, 0x50, 0x50, 0x50, 0x3C}, /* y */
    {0x44, 0x64, 0x54, 0x4C, 0x44}, /* z */
    {0x00, 0x08, 0x36, 0x41, 0x00}, /* { */
    {0x00, 0x00, 0x7F, 0x00, 0x00}, /* | */
    {0x00, 0x41, 0x36, 0x08, 0x00}, /* } */
    {0x08, 0x08, 0x2A, 0x1C, 0x08}  /* ~ */
};

/* Послідовність команд ініціалізації дисплея SSD1306 (128x64) */
static const uint8_t ssd1306_init_seq[] = {
    0xAE,       /* Display OFF */
    0xD5, 0x80, /* Set Display Clock Divide Ratio / Oscillator Frequency */
    0xA8, 0x3F, /* Set Multiplex Ratio (1 to 64) -> 64MUX */
    0xD3, 0x00, /* Set Display Offset = 0 */
    0x40,       /* Set Display Start Line = 0 */
    0x8D, 0x14, /* Enable Charge Pump */
    0x20, 0x00, /* Memory Addressing Mode = Horizontal */
    0xA1,       /* Segment Re-map = col 127 mapped to SEG0 */
    0xC8,       /* COM Output Scan Direction = remapped */
    0xDA, 0x12, /* Set COM Pins Hardware Configuration */
    0x81, 0xCF, /* Set Contrast Control */
    0xD9, 0xF1, /* Set Pre-charge Period */
    0xDB, 0x40, /* Set VCOMH Deselect Level */
    0xA4,       /* Entire Display ON (Resume to RAM content) */
    0xA6,       /* Set Normal Display (non-inverted) */
    0xAF        /* Display ON */
};

ssd1306_err_t ssd1306_init(ssd1306_t *disp, uint8_t i2c_addr) {
    if (disp == NULL) return SSD1306_ERR_PARAM;

    disp->i2c_addr = i2c_addr;
    disp->is_initialized = false;
    ssd1306_clear(disp);

    /* Перевірка наявності дисплея */
    if (!i2c_ping(disp->i2c_addr)) {
        return SSD1306_ERR_I2C;
    }

    /* Відправка команд ініціалізації по I2C з префіксом Control Byte = 0x00 */
    for (size_t i = 0; i < sizeof(ssd1306_init_seq); i++) {
        uint8_t cmd_packet[2] = { 0x00, ssd1306_init_seq[i] };
        if (i2c_write(disp->i2c_addr, cmd_packet, 2, 100) != I2C_OK) {
            return SSD1306_ERR_I2C;
        }
    }

    disp->is_initialized = true;
    ssd1306_update(disp);
    return SSD1306_OK;
}

void ssd1306_clear(ssd1306_t *disp) {
    if (disp == NULL) return;
    memset(disp->buffer, 0x00, sizeof(disp->buffer));
}

ssd1306_err_t ssd1306_update(ssd1306_t *disp) {
    if (disp == NULL || !disp->is_initialized) return SSD1306_ERR_PARAM;

    /* Встановлення адреси колонок (0..127) та сторінок (0..7) */
    uint8_t setup_cmds[] = {
        0x00, 0x21, 0, 127, /* Column Address Range */
        0x00, 0x22, 0, 7    /* Page Address Range */
    };

    for (size_t i = 0; i < sizeof(setup_cmds); i += 2) {
        if (i2c_write(disp->i2c_addr, &setup_cmds[i], 2, 100) != I2C_OK) {
            return SSD1306_ERR_I2C;
        }
    }

    /* Відправка буфера кадра блоками по 64 байти з префіксом Co=0, D/C#=1 (0x40) */
    uint8_t tx_buf[65];
    tx_buf[0] = 0x40; /* Data continuation byte */

    for (size_t i = 0; i < SSD1306_BUFFER_SIZE; i += 64) {
        memcpy(&tx_buf[1], &disp->buffer[i], 64);
        if (i2c_write(disp->i2c_addr, tx_buf, 65, 100) != I2C_OK) {
            return SSD1306_ERR_I2C;
        }
    }

    return SSD1306_OK;
}

void ssd1306_draw_pixel(ssd1306_t *disp, int16_t x, int16_t y, ssd1306_color_t color) {
    if (disp == NULL || x < 0 || x >= SSD1306_WIDTH || y < 0 || y >= SSD1306_HEIGHT) {
        return;
    }

    size_t index = x + (y / 8) * SSD1306_WIDTH;
    uint8_t bit_mask = 1U << (y % 8);

    if (color == SSD1306_COLOR_WHITE) {
        disp->buffer[index] |= bit_mask;
    } else if (color == SSD1306_COLOR_BLACK) {
        disp->buffer[index] &= ~bit_mask;
    } else if (color == SSD1306_COLOR_INVERT) {
        disp->buffer[index] ^= bit_mask;
    }
}

void ssd1306_draw_line(ssd1306_t *disp, int16_t x0, int16_t y0, int16_t x1, int16_t y1, ssd1306_color_t color) {
    int16_t dx = abs(x1 - x0);
    int16_t sx = (x0 < x1) ? 1 : -1;
    int16_t dy = -abs(y1 - y0);
    int16_t sy = (y0 < y1) ? 1 : -1;
    int16_t err = dx + dy;

    while (1) {
        ssd1306_draw_pixel(disp, x0, y0, color);
        if (x0 == x1 && y0 == y1) break;
        int16_t e2 = 2 * err;
        if (e2 >= dy) { err += dy; x0 += sx; }
        if (e2 <= dx) { err += dx; y0 += sy; }
    }
}

void ssd1306_draw_circle(ssd1306_t *disp, int16_t x0, int16_t y0, int16_t r, ssd1306_color_t color) {
    int16_t f = 1 - r;
    int16_t ddF_x = 1;
    int16_t ddF_y = -2 * r;
    int16_t x = 0;
    int16_t y = r;

    ssd1306_draw_pixel(disp, x0, y0 + r, color);
    ssd1306_draw_pixel(disp, x0, y0 - r, color);
    ssd1306_draw_pixel(disp, x0 + r, y0, color);
    ssd1306_draw_pixel(disp, x0 - r, y0, color);

    while (x < y) {
        if (f >= 0) {
            y--;
            ddF_y += 2;
            f += ddF_y;
        }
        x++;
        ddF_x += 2;
        f += ddF_x;

        ssd1306_draw_pixel(disp, x0 + x, y0 + y, color);
        ssd1306_draw_pixel(disp, x0 - x, y0 + y, color);
        ssd1306_draw_pixel(disp, x0 + x, y0 - y, color);
        ssd1306_draw_pixel(disp, x0 - x, y0 - y, color);
        ssd1306_draw_pixel(disp, x0 + y, y0 + x, color);
        ssd1306_draw_pixel(disp, x0 - y, y0 + x, color);
        ssd1306_draw_pixel(disp, x0 + y, y0 - x, color);
        ssd1306_draw_pixel(disp, x0 - y, y0 - x, color);
    }
}

void ssd1306_draw_filled_circle(ssd1306_t *disp, int16_t x0, int16_t y0, int16_t r, ssd1306_color_t color) {
    for (int16_t y = -r; y <= r; y++) {
        for (int16_t x = -r; x <= r; x++) {
            if (x * x + y * y <= r * r) {
                ssd1306_draw_pixel(disp, x0 + x, y0 + y, color);
            }
        }
    }
}

void ssd1306_draw_char(ssd1306_t *disp, int16_t x, int16_t y, char c, ssd1306_color_t color) {
    if (c < 0x20 || c > 0x7E) c = '?';
    uint8_t idx = (uint8_t)(c - 0x20);

    for (uint8_t col = 0; col < 5; col++) {
        uint8_t line = font5x7[idx][col];
        for (uint8_t row = 0; row < 7; row++) {
            if (line & (1U << row)) {
                ssd1306_draw_pixel(disp, x + col, y + row, color);
            }
        }
    }
}

void ssd1306_draw_string(ssd1306_t *disp, int16_t x, int16_t y, const char *str, ssd1306_color_t color) {
    if (str == NULL) return;
    int16_t cur_x = x;
    while (*str) {
        ssd1306_draw_char(disp, cur_x, y, *str, color);
        cur_x += 6; /* 5 пікселів символ + 1 інтервал */
        str++;
    }
}

void ssd1306_draw_compass(ssd1306_t *disp, int16_t cx, int16_t cy, int16_t radius, float heading_deg) {
    if (disp == NULL) return;

    /* 1. Малювання кругового циферблата компаса */
    ssd1306_draw_circle(disp, cx, cy, radius, SSD1306_COLOR_WHITE);
    ssd1306_draw_filled_circle(disp, cx, cy, 2, SSD1306_COLOR_WHITE);

    /* 2. Позначки сторін світу на циферблаті (N, S, E, W) */
    ssd1306_draw_char(disp, cx - 2, cy - radius + 2, 'N', SSD1306_COLOR_WHITE);
    ssd1306_draw_char(disp, cx - 2, cy + radius - 8, 'S', SSD1306_COLOR_WHITE);
    ssd1306_draw_char(disp, cx + radius - 7, cy - 3, 'E', SSD1306_COLOR_WHITE);
    ssd1306_draw_char(disp, cx - radius + 2, cy - 3, 'W', SSD1306_COLOR_WHITE);

    /* 3. Перетворення азимута в кут вектора напрямку на екранних координатах */
    float rad = heading_deg * (M_PI / 180.0f);

    /* Запевняємо, що стрілка показує Північ відносного повороту */
    int16_t arrow_length = radius - 4;
    int16_t tip_x = cx + (int16_t)roundf(arrow_length * sinf(rad));
    int16_t tip_y = cy - (int16_t)roundf(arrow_length * cosf(rad));

    int16_t tail_x = cx - (int16_t)roundf((arrow_length / 2) * sinf(rad));
    int16_t tail_y = cy + (int16_t)roundf((arrow_length / 2) * cosf(rad));

    /* Малювання стрижня стрілки */
    ssd1306_draw_line(disp, cx, cy, tip_x, tip_y, SSD1306_COLOR_WHITE);

    /* Малювання наконечника стрілки (бічні вусики під кутом 150°) */
    float left_wing_rad = rad + (150.0f * (M_PI / 180.0f));
    float right_wing_rad = rad - (150.0f * (M_PI / 180.0f));

    int16_t left_x = tip_x + (int16_t)roundf(5.0f * sinf(left_wing_rad));
    int16_t left_y = tip_y - (int16_t)roundf(5.0f * cosf(left_wing_rad));

    int16_t right_x = tip_x + (int16_t)roundf(5.0f * sinf(right_wing_rad));
    int16_t right_y = tip_y - (int16_t)roundf(5.0f * cosf(right_wing_rad));

    ssd1306_draw_line(disp, tip_x, tip_y, left_x, left_y, SSD1306_COLOR_WHITE);
    ssd1306_draw_line(disp, tip_x, tip_y, right_x, right_y, SSD1306_COLOR_WHITE);

    /* Лінія до південного кінця (пунктирна / тонка) */
    ssd1306_draw_line(disp, cx, cy, tail_x, tail_y, SSD1306_COLOR_WHITE);
}
