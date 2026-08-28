#include <stdint.h>

// RS = A16: коли біт A16 = 0 -> команда, = 1 -> дані.
// Різниця адрес = 2^16 = 0x20000 (бо A16 важить 2^16).
#define LCD_CMD   (*(volatile uint16_t *)0x60000000)   // A16 = 0  -> регістр команд
#define LCD_DATA  (*(volatile uint16_t *)0x60020000)   // A16 = 1  -> регістр даних

static inline void lcd_write_cmd(uint16_t c)  { LCD_CMD  = c; }  // один цикл шини!
static inline void lcd_write_data(uint16_t d) { LCD_DATA = d; }

void lcd_pixel(uint16_t color) {
    lcd_write_cmd(0x2C);        // команда «пиши в пам'ять дисплея»
    lcd_write_data(color);      // саме піксельне слово (RGB565)
}
