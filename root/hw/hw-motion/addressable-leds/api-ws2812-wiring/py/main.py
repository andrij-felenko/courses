# MicroPython на ESP32: модуль neopixel сам витримує таймінг WS2812.
from machine import Pin
from neopixel import NeoPixel

PIN = 5          # GPIO даних (через рівнезсув на DIN стрічки)
N   = 100        # кількість пікселів у стрічці

strip = NeoPixel(Pin(PIN, Pin.OUT), N)   # порядок байтів G-R-B — типовий для WS2812

scale = 40                               # обмежуємо яскравість вручну: 40/255 ≈ 0.16 струму
r, g, b = 255, 0, 0                       # перший піксель — червоний
strip[0] = (r * scale // 255, g * scale // 255, b * scale // 255)
strip.write()                            # вилити кадр у стрічку + скидання (LOW ≥ 50 мкс)
