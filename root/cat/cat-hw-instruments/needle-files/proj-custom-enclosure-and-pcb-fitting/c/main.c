#include <stdio.h>
#include <stdlib.h>
#include "oled.h"

// Буфер кадру для 128x64 монохромного OLED-дисплея
static uint8_t oled_buffer[OLED_BUF_SIZE];

bool oled_init(void) {
    oled_clear();
    return true;
}

void oled_clear(void) {
    for (size_t i = 0; i < OLED_BUF_SIZE; i++) {
        oled_buffer[i] = 0x00;
    }
}

void oled_draw_pixel(uint8_t x, uint8_t y, oled_pixel_state_t state) {
    if (x >= OLED_WIDTH || y >= OLED_HEIGHT) {
        return; // Захист від виходу за межі буфера
    }

    uint16_t idx = x + (y / 8) * OLED_WIDTH;
    uint8_t bit = y % 8;

    if (state == PIXEL_ON) {
        oled_buffer[idx] |= (1 << bit);
    } else {
        oled_buffer[idx] &= ~(1 << bit);
    }
}

void oled_draw_line(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1, oled_pixel_state_t state) {
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int sx = (x0 < x1) ? 1 : -1;
    int sy = (y0 < y1) ? 1 : -1;
    int err = dx - dy;

    while (1) {
        oled_draw_pixel(x0, y0, state);
        if (x0 == x1 && y0 == y1) break;
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

void oled_draw_rect(uint8_t x, uint8_t y, uint8_t w, uint8_t h, oled_pixel_state_t state) {
    if (w == 0 || h == 0) return;
    
    uint8_t x2 = x + w - 1;
    uint8_t y2 = y + h - 1;

    oled_draw_line(x, y, x2, y, state);   // Верхня межа
    oled_draw_line(x, y2, x2, y2, state); // Нижня межа
    oled_draw_line(x, y, x, y2, state);   // Ліва межа
    oled_draw_line(x2, y, x2, y2, state); // Права межа
}

void oled_update(void) {
    printf("OLED кадр оновлено: тестову контурну рамку виведено на дисплей.\n");
}

int main(void) {
    if (!oled_init()) {
        fprintf(stderr, "Помилка ініціалізації OLED-дисплея\n");
        return EXIT_FAILURE;
    }

    // Очищуємо буфер
    oled_clear();

    // 1. Побудова зовнішньої рамки точно по межах активної зони екрана (128x64).
    // Якщо при підгонці вирізу надфілем крайній шар пікселів ховається під фаскою
    // чи стінкою корпусу, виріз потрібно розширити відповідним надфілем.
    oled_draw_rect(0, 0, OLED_WIDTH, OLED_HEIGHT, PIXEL_ON);

    // 2. Додавання центрального прицілу для контролю симетрії установки дисплея
    uint8_t center_x = OLED_WIDTH / 2;
    uint8_t center_y = OLED_HEIGHT / 2;

    oled_draw_line(center_x - 10, center_y, center_x + 10, center_y, PIXEL_ON);
    oled_draw_line(center_x, center_y - 10, center_x, center_y + 10, PIXEL_ON);

    // 3. Вивід згенерованого шаблону на екран
    oled_update();

    return EXIT_SUCCESS;
}
