#include <stdint.h>

#define LCD_W  240
#define LCD_H  320

// Задати прямокутне вікно виводу [x0..x1] × [y0..y1].
static void lcd_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    lcd_write_cmd(0x2A);                     // Column address set
    lcd_write_data(x0 >> 8); lcd_write_data(x0 & 0xFF);
    lcd_write_data(x1 >> 8); lcd_write_data(x1 & 0xFF);

    lcd_write_cmd(0x2B);                     // Page (row) address set
    lcd_write_data(y0 >> 8); lcd_write_data(y0 & 0xFF);
    lcd_write_data(y1 >> 8); lcd_write_data(y1 & 0xFF);

    lcd_write_cmd(0x2C);                     // Memory write — далі йдуть пікселі
}

// Залити весь екран суцільним кольором. Ось воно — ядро задачі.
void lcd_fill_screen(uint16_t color) {
    lcd_set_window(0, 0, LCD_W - 1, LCD_H - 1);
    for (uint32_t i = 0; i < (uint32_t)LCD_W * LCD_H; ++i)
        lcd_write_data(color);               // 76 800 циклів шини — і екран залито
}

// Залити довільний прямокутник (напр. очистити рядок списку).
void lcd_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color) {
    if (w == 0 || h == 0) return;
    lcd_set_window(x, y, x + w - 1, y + h - 1);
    for (uint32_t i = 0; i < (uint32_t)w * h; ++i)
        lcd_write_data(color);
}

// Вивести готовий буфер зображення (напр. кадр з RAM або спрайт).
void lcd_blit(uint16_t x, uint16_t y, uint16_t w, uint16_t h, const uint16_t *pix) {
    lcd_set_window(x, y, x + w - 1, y + h - 1);
    const uint32_t n = (uint32_t)w * h;
    for (uint32_t i = 0; i < n; ++i)
        lcd_write_data(pix[i]);
}
