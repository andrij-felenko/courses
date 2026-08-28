# --- Ky034: неблокуючий драйвер увімкнення для самограйного RGB-модуля ---
# Керує ЛИШЕ ввімкненням/вимкненням (кольором KY-034 керувати не можна).
from machine import Pin
import time

SOLID, BLINK, BURST = 0, 1, 2

class Ky034:
    def __init__(self, pin):
        self._pin  = Pin(pin, Pin.OUT)
        self._mode = SOLID
        self._is_on = False
        self._last  = time.ticks_ms()
        self._on_ms = self._off_ms = 500
        self._half_ms = 200
        self._left  = 0
        self._write(False)

    def _write(self, on_state):
        self._is_on = on_state
        self._pin.value(1 if on_state else 0)

    # Постійно ввімкнути / вимкнути
    def on(self):  self._mode = SOLID; self._write(True)
    def off(self): self._mode = SOLID; self._write(False)

    # Рівне блимання: on_ms горить, off_ms згас
    def blink(self, on_ms, off_ms):
        self._on_ms, self._off_ms = on_ms, off_ms
        self._mode = BLINK
        self._last = time.ticks_ms()
        self._write(True)

    # Пачка з n спалахів по half_ms на півфазу, тоді сама затихає
    def burst(self, n, half_ms):
        self._left = n * 2             # n спалахів = 2·n перемикань
        self._half_ms = half_ms
        self._mode = BURST
        self._last = time.ticks_ms()
        self._write(True)

    def busy(self):
        return self._mode == BURST and self._left > 0

    # Смикати в КОЖНІЙ ітерації циклу. Нічого не блокує.
    def tick(self):
        if self._mode == SOLID:
            return
        now = time.ticks_ms()

        if self._mode == BLINK:
            phase = self._on_ms if self._is_on else self._off_ms
            if time.ticks_diff(now, self._last) >= phase:
                self._last = now
                self._write(not self._is_on)
            return

        # BURST
        if self._left > 0 and time.ticks_diff(now, self._last) >= self._half_ms:
            self._last = now
            self._left -= 1
            if self._left == 0:
                self._write(False); self._mode = SOLID   # пачка добігла — гасимо
            else:
                self._write(not self._is_on)

# ---------- використання ----------
lamp = Ky034(5)                        # модуль на GPIO5
btn  = Pin(4, Pin.IN, Pin.PULL_UP)
lamp.blink(500, 500)                   # тлом — рівно блимає

was_pressed = False
while True:
    pressed = (btn.value() == 0)
    if pressed and not was_pressed and not lamp.busy():
        lamp.burst(3, 150)             # натиск → блимнути тричі поверх усього
    was_pressed = pressed

    lamp.tick()                        # єдиний обов'язок: смикати щоцикл
    # ...тут будь-яка інша логіка, вона не блокована
