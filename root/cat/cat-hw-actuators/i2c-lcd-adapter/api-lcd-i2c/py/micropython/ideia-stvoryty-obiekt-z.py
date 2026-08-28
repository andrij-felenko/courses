from machine import I2C, Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd            # драйвер PCF8574-адаптера для HD44780

# На ESP32/STM32/Pico свою шину піднімаємо САМІ: задаємо ніжки прямо тут.
i2c = I2C(0, sda=Pin(21), scl=Pin(22))   # SDA=21, SCL=22 — приклад для ESP32

# (шина, адреса, рядки, стовпці). Адресу взяли зі сканера!
lcd = I2cLcd(i2c, 0x27, 2, 16)           # конструктор сам робить init + backlight

lcd.move_to(0, 0)                        # стовпець 0, рядок 0 (відлік із нуля)
lcd.putstr("Hello, world!")

lcd.move_to(0, 1)                        # другий рядок
lcd.putstr("I2C LCD 1602")

# усе вже на екрані — далі скрипту нічого робити
