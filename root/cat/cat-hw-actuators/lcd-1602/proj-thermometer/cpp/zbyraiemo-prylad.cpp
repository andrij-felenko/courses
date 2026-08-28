#include <LiquidCrystal.h>

LiquidCrystal lcd(8, 9, 4, 5, 6, 7);   // rs, e, d4, d5, d6, d7

// Значок градуса у комірку CGRAM №0
byte degree[8] = {
    0b01100, 0b10010, 0b10010, 0b01100,
    0b00000, 0b00000, 0b00000, 0b00000
};

void setup() {
    lcd.begin(16, 2);
    lcd.createChar(0, degree);      // записати «°» — обов'язково після begin()

    // Сталу «шапку» малюємо ОДИН раз; далі оновлюємо лише змінні поля
    lcd.setCursor(0, 0);
    lcd.print("Temp:      ");        // "Temp:" + місце під число
    lcd.setCursor(0, 1);
    lcd.print("Uptime: 00:00");
}
