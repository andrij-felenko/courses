from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms

RGB_PIN = 48                          # вбудований WS2812 на SuperMini
np = NeoPixel(Pin(RGB_PIN), 1)        # один діод на цьому виводі

# зелений на повну; порядок — R, G, B (0..255)
np[0] = (0, 40, 0)                    # не 255 — діод яскравий, 40 досить
np.write()

while True:
    np[0] = (40, 0, 0)               # червоний
    np.write()
    sleep_ms(500)
    np[0] = (0, 0, 40)               # синій
    np.write()
    sleep_ms(500)
