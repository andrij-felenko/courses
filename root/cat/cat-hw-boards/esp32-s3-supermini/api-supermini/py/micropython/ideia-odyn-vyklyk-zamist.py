from machine import Pin
from neopixel import NeoPixel
import time

RGB_PIN = 48   # вбудований WS2812 на SuperMini

np = NeoPixel(Pin(RGB_PIN), 1)   # один діод у ланцюжку

np[0] = (0, 0, 0)                # згасити на старті
np.write()

while True:
    np[0] = (30, 0, 0)           # червоний
    np.write()
    time.sleep_ms(400)
    np[0] = (0, 30, 0)           # зелений
    np.write()
    time.sleep_ms(400)
    np[0] = (0, 0, 30)           # синій
    np.write()
    time.sleep_ms(400)
