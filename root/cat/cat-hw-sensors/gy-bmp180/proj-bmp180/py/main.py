import time
import board
import bmp180

i2c = board.I2C()          # на ESP32/Pico — busio.I2C зі своїми ніжками
bmp = bmp180.BMP180(i2c)   # читає 0x55, тягне всі 11 коефіцієнтів

while True:
    print("T = {} C   P = {} hPa   h = {} m".format(
        bmp.temperature,   # °C, float
        bmp.pressure,      # гПа (у CircuitPython — уже гектопаскалі, не Па!)
        bmp.altitude))     # м
    time.sleep(1)
