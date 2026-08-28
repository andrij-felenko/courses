from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

i2c = I2C(0, sda=Pin(21), scl=Pin(22))   # свої ніжки — до конструктора (див. задачу 2)
lcd = I2cLcd(i2c, 0x27, 2, 16)

last_shown = -1                # яке число вже на екрані (-1 = «ще нічого»)

# СТАТИЧНУ частину малюємо РАЗ, тут, а не в циклі:
lcd.move_to(0, 0)
lcd.putstr("Uptime:")
lcd.move_to(0, 1)
lcd.putstr("sec = ")

while True:
    sec = time.ticks_ms() // 1000

    if sec != last_shown:          # змінилось? тільки тоді чіпаємо екран
        lcd.move_to(6, 1)          # одразу після "sec = "
        lcd.putstr("{}   ".format(sec))   # число + пробіли, щоб затерти «хвіст»
        last_shown = sec

    # тут може крутитися будь-яка інша робота — екран її не гальмує
