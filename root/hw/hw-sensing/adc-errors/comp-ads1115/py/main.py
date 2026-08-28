import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1115 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)   # ADDR -> GND
ads.gain = 1                            # PGA ±4.096 В (той самий FSR, що в CFG)
ads.mode = Mode.SINGLE                  # single-shot; драйвер сам чекає 1/DR

chan = AnalogIn(ads, ADS.P0)            # A0 проти GND (несиметрично)

raw = chan.value        # 16-бітний код зі знаком; читання саме запускає перетворення
volts = chan.voltage    # драйвер уже множить на FSR/32768 і повертає вольти
