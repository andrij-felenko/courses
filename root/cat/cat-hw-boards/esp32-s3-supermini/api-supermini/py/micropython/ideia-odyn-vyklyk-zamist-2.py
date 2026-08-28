from machine import Pin
from neopixel import NeoPixel

RGB_PIN = 48
np = NeoPixel(Pin(RGB_PIN), 1)

def _show(r, g, b):
    np[0] = (r, g, b)
    np.write()

def status_ok():    _show(0, 30, 0)    # зелений — усе добре
def status_busy():  _show(30, 20, 0)   # бурштин — працюю
def status_error(): _show(40, 0, 0)    # червоний — помилка
def status_off():   _show(0, 0, 0)     # згас
