#include <stdint.h>

// Один запис у регістр команд — рівно один цикл шини на ~NE1 із D/C = 0.
static inline void lcd_write_cmd(uint16_t cmd) {
    LCD_CMD = cmd;
}

// Один запис у регістр даних — цикл шини з D/C = 1 (аргумент або піксель).
static inline void lcd_write_data(uint16_t data) {
    LCD_DATA = data;
}

// Читання (напр. ID дисплея) — той самий цикл, але ~RD замість ~WR.
static inline uint16_t lcd_read_data(void) {
    return LCD_DATA;
}

// Найчастіший шаблон: команда, за якою йде кілька байтів-аргументів.
static void lcd_cmd_args(uint16_t cmd, const uint8_t *args, int n) {
    lcd_write_cmd(cmd);
    for (int i = 0; i < n; ++i)
        lcd_write_data(args[i]);          // аргументи 8-бітні, але шлемо як слова
}
