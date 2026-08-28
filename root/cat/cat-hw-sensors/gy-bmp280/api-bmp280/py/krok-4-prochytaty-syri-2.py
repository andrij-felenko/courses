import time
import board
import adafruit_bmp280

i2c = board.I2C()   # (на ESP32/Pico — busio.I2C зі своїми ніжками)

# Конструктор сам читає ідентифікатор чипа з 0xD0 і калібрування від 0x88,
# а на чужому чипі чи мовчазній шині підніме виняток — тож окремі
# who_am_i / read_calibration / configure згортаються в один рядок.
try:
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
except (ValueError, RuntimeError):
    print("Це не BMP280 (або давач мовчить). Стоп.")
    while True:
        time.sleep(1)

bmp280.overscan_temperature = adafruit_bmp280.OVERSCAN_X2   # передискретизація,
bmp280.overscan_pressure = adafruit_bmp280.OVERSCAN_X16     # фільтр, режим
bmp280.iir_filter = adafruit_bmp280.IIR_FILTER_X16
bmp280.mode = adafruit_bmp280.MODE_NORMAL
print("BMP280 готовий.")

while True:
    print("T = {:.2f} C   P = {:.2f} hPa".format(
        bmp280.temperature, bmp280.pressure))
    time.sleep(1)
