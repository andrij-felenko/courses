#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

long lastShown = -1;         // яке число вже на екрані (-1 = «ще нічого»)

void setup() {
  Wire.begin(21, 22);        // свої ніжки — до init() (див. задачу 2)
  lcd.init();
  lcd.backlight();

  // СТАТИЧНУ частину малюємо РАЗ, тут, а не в циклі:
  lcd.setCursor(0, 0);
  lcd.print("Uptime:");
  lcd.setCursor(0, 1);
  lcd.print("sec = ");
}

void loop() {
  long sec = millis() / 1000;

  if (sec != lastShown) {        // змінилось? тільки тоді чіпаємо екран
    lcd.setCursor(6, 1);         // одразу після "sec = "
    lcd.print(sec);
    lcd.print("   ");            // затерти «хвіст» від коротшого числа
    lastShown = sec;
  }

  // тут може крутитися будь-яка інша робота — екран її не гальмує
}
