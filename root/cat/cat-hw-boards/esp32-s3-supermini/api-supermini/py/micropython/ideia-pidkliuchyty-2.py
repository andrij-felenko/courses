from machine import Pin, I2C
from bmp280 import BMP280   # micropython-bmp280
import time

SDA_PIN = 8
SCL_PIN = 9
BMP_ADDR = 0x76

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=100000)

# Конструктор сам прочитає ідентифікатор і кине виняток, якщо чипа немає
# або адреса не та — тому перевіряти результат обов'язково.
try:
    bmp = BMP280(i2c, addr=BMP_ADDR)
except OSError:
    print("BMP280 не знайдено за 0x76. Пробую 0x77...")
    try:
        bmp = BMP280(i2c, addr=0x77)
    except OSError:
        print("Не знайдено ні за 0x76, ні за 0x77. Перевір дроти.")
        while True:
            time.sleep(1)   # далі йти нема сенсу

# Розумні налаштування для метеозадачі: помірне усереднення, рідкі виміри.
bmp.oversample(BMP280.OVERSAMPLE_16)   # тиск ×16 (точніше)
bmp.use_case(BMP280.BMP280_CASE_WEATHER)
print("BMP280 готовий.")

while True:
    temp_c = bmp.temperature        # °C
    pres_pa = bmp.pressure          # Па
    pres_hpa = pres_pa / 100.0      # гПа (мілібари) — звичніші одиниці

    print("t = {:.2f} °C   p = {:.1f} гПа".format(temp_c, pres_hpa))
    time.sleep(1)
