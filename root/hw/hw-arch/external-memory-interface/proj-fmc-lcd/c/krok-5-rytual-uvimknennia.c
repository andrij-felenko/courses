#include <stdint.h>

// Проста затримка. У бойовому коді — від системного таймера; тут спрощено.
extern void delay_ms(uint32_t ms);

// Апаратне скидання дисплея смикає окремий GPIO ~RESET (не через FMC!).
extern void lcd_hw_reset_pin(int level);   // 1 = високий, 0 = низький

void lcd_reset(void) {
    lcd_hw_reset_pin(1); delay_ms(5);
    lcd_hw_reset_pin(0); delay_ms(20);      // тримаємо в скиданні ≥ 10 мкс, з запасом
    lcd_hw_reset_pin(1); delay_ms(150);     // після відпускання даємо контролеру ожити
}

void ili9341_init(void) {
    lcd_reset();

    lcd_write_cmd(0x01);                     // Software reset
    delay_ms(150);

    // --- службові команди «розгону» живлення (значення з даташита/драйвера) ---
    { const uint8_t a[] = {0x03, 0x80, 0x02};       lcd_cmd_args(0xEF, a, 3); }
    { const uint8_t a[] = {0x00, 0xC1, 0x30};       lcd_cmd_args(0xCF, a, 3); }
    { const uint8_t a[] = {0x64, 0x03, 0x12, 0x81}; lcd_cmd_args(0xED, a, 4); }
    { const uint8_t a[] = {0x85, 0x00, 0x78};       lcd_cmd_args(0xE8, a, 3); }
    { const uint8_t a[] = {0x39, 0x2C, 0x00, 0x34, 0x02}; lcd_cmd_args(0xCB, a, 5); }
    { const uint8_t a[] = {0x20};                   lcd_cmd_args(0xF7, a, 1); }
    { const uint8_t a[] = {0x00, 0x00};             lcd_cmd_args(0xEA, a, 2); }

    // --- керування напругами живлення й VCOM ---
    { const uint8_t a[] = {0x23};                   lcd_cmd_args(0xC0, a, 1); } // Power control 1
    { const uint8_t a[] = {0x10};                   lcd_cmd_args(0xC1, a, 1); } // Power control 2
    { const uint8_t a[] = {0x3E, 0x28};             lcd_cmd_args(0xC5, a, 2); } // VCOM 1
    { const uint8_t a[] = {0x86};                   lcd_cmd_args(0xC7, a, 1); } // VCOM 2

    // --- орієнтація та формат пікселя ---
    { const uint8_t a[] = {0x48};                   lcd_cmd_args(0x36, a, 1); } // MADCTL: порядок рядків/колонок і RGB
    { const uint8_t a[] = {0x55};                   lcd_cmd_args(0x3A, a, 1); } // PIXFMT: 0x55 = 16 біт/піксель (RGB565)

    // --- частота кадру, функції дисплея, гама ---
    { const uint8_t a[] = {0x00, 0x18};             lcd_cmd_args(0xB1, a, 2); } // Frame rate
    { const uint8_t a[] = {0x08, 0x82, 0x27};       lcd_cmd_args(0xB6, a, 3); } // Display function control
    { const uint8_t a[] = {0x00};                   lcd_cmd_args(0xF2, a, 1); } // 3Gamma off
    { const uint8_t a[] = {0x01};                   lcd_cmd_args(0x26, a, 1); } // Gamma curve 1

    { const uint8_t gp[] = {0x0F,0x31,0x2B,0x0C,0x0E,0x08,0x4E,0xF1,
                            0x37,0x07,0x10,0x03,0x0E,0x09,0x00};
      lcd_cmd_args(0xE0, gp, 15); }                  // позитивна гама
    { const uint8_t gn[] = {0x00,0x0E,0x14,0x03,0x11,0x07,0x31,0xC1,
                            0x48,0x08,0x0F,0x0C,0x31,0x36,0x0F};
      lcd_cmd_args(0xE1, gn, 15); }                  // негативна гама

    lcd_write_cmd(0x11);                     // Sleep out — вихід зі сну
    delay_ms(150);                           // обов'язкова пауза: генератори напруги розганяються
    lcd_write_cmd(0x29);                     // Display ON — і аж тепер матриця світиться
    delay_ms(50);
}
