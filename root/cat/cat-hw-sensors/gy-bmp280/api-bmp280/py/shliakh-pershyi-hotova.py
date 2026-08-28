import time
import board
import adafruit_bmp280

i2c = board.I2C()   # використовує board.SCL і board.SDA
# На платах, де стандартні ніжки не ті, шину задають явно, напр.:
#   import busio
#   i2c = busio.I2C(board.GP5, board.GP4)   # SCL=GP5, SDA=GP4 — типово для Pico

# УВАГА: типова плата GY-BMP280 сидить на 0x76, а не на «рідній» 0x77 —
# тому адресу задаємо явно (за замовчуванням бібліотека взяла б 0x77).
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

# Один раз налаштувати режим виміру: неперервний, обидва канали з
# передискретизацією, помірний згладжувальний фільтр.
bmp280.mode = adafruit_bmp280.MODE_NORMAL          # міряє сам, без запитів
bmp280.overscan_temperature = adafruit_bmp280.OVERSCAN_X2    # температура ×2
bmp280.overscan_pressure = adafruit_bmp280.OVERSCAN_X16      # тиск ×16 (найважливіше)
bmp280.iir_filter = adafruit_bmp280.IIR_FILTER_X16          # сильний IIR-фільтр
bmp280.standby_period = adafruit_bmp280.STANDBY_TC_500      # пауза 500 мс між вимірами
bmp280.sea_level_pressure = 1013.25                # опорний тиск для висоти, гПа

while True:
    t = bmp280.temperature   # °C
    p = bmp280.pressure      # гПа (у CircuitPython — уже гектопаскалі!)
    h = bmp280.altitude      # м, відносно sea_level_pressure

    print("T = {:.2f} C   P = {:.2f} hPa   h = {:.1f} m".format(t, p, h))
    time.sleep(1)
