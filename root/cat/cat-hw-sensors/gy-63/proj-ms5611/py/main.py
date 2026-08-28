# MicroPython (Pico/ESP32): драйвер micropython-ms5611 (jposada202020) —
# аналог RobTillaart, теж ховає скид, читання PROM, паузи й обидва порядки компенсації.
#   pip install micropython-ms5611  (або скопіювати модуль на плату)
import time
from math import pow
from machine import Pin, I2C
from micropython_ms5611 import ms5611

sea_level_hPa = 1013.25          # опорний тиск на рівні моря; уточнимо його нижче

# Ніжки шини задаємо тут-таки: SDA=21, SCL=22 — типово для ESP32 (на Pico свої).
i2c  = I2C(0, sda=Pin(21), scl=Pin(22))
# Конструктор приймає адресу; 0x77 — коли CSB вільний або на GND, 0x76 — на VCC.
baro = ms5611.MS5611(i2c, 0x77)  # кине RuntimeError, якщо давач не відповів

# Режим згладжування: PRESS_OSR_4096 — найдовша пауза ~9 мс, роздільність
# ~0.012 мбар (ті самі «10 см»); є й швидші PRESS_OSR_256 … PRESS_OSR_2048.
baro.pressure_oversample_rate    = ms5611.PRESS_OSR_4096
baro.temperature_oversample_rate = ms5611.TEMP_OSR_4096

while True:
    t, p_kPa = baro.measurements      # повний вимір: обидва порядки компенсації
    p = p_kPa * 10.0                  # драйвер віддає кПа → у гПа (мбар)
    # висоти в драйвері немає — рахуємо тією самою барометричною формулою:
    h = 44330.0 * (1.0 - pow(p / sea_level_hPa, 0.1903))

    print("T = {:.2f} °C   P = {:.2f} hPa   h = {:.1f} m".format(t, p, h))
    time.sleep(1)
