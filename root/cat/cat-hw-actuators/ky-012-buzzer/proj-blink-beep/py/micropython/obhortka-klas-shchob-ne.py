# --- Buzzer: неблокуючий драйвер активного зумера (KY-012 і подібних) ---
# Керує ЛИШЕ ввімкненням/вимкненням: висоту тону змінити не можна.
from machine import Pin
import time

SOLID, ONESHOT, SERIES = 0, 1, 2

class Buzzer:
    def __init__(self, pin):
        self._pin  = Pin(pin, Pin.OUT)
        self._mode = SOLID
        self._is_on = False
        self._until = 0
        self._last  = time.ticks_ms()
        self._half  = 100
        self._left  = 0
        self._write(False)

    def _write(self, on_state):
        self._is_on = on_state
        self._pin.value(1 if on_state else 0)   # HIGH-тригер: 1 пищить

    # Один біп на ms мс.
    def beep(self, ms):
        self._mode = ONESHOT
        self._write(True)
        self._until = time.ticks_add(time.ticks_ms(), ms)

    # Серія з n біпів по half мс на півфазу, тоді сама затихає.
    def series(self, n, half):
        self._mode = SERIES
        self._left = n * 2                # n біпів = 2·n перемикань
        self._half = half
        self._last = time.ticks_ms()
        self._write(True)

    # Безперервний тон, доки не викличеш stop(). Для тривоги.
    def on(self):   self._mode = SOLID; self._write(True)
    def stop(self): self._mode = SOLID; self._write(False)

    def busy(self):
        return self._mode == SERIES and self._left > 0

    # Смикати в КОЖНІЙ ітерації. Нічого не блокує.
    def update(self):
        now = time.ticks_ms()

        if self._mode == ONESHOT:
            if self._is_on and time.ticks_diff(now, self._until) >= 0:
                self._write(False); self._mode = SOLID
            return
        if self._mode == SERIES:
            if self._left > 0 and time.ticks_diff(now, self._last) >= self._half:
                self._last = now
                self._left -= 1
                if self._left == 0:
                    self._write(False); self._mode = SOLID   # серія добігла — тиша
                else:
                    self._write(not self._is_on)
            return
        # SOLID — тримаємо заданий стан

# ---------- використання ----------
buz = Buzzer(8)                      # модуль на пін 8
btn = Pin(2, Pin.IN, Pin.PULL_UP)

was_pressed = False
while True:
    pressed = (btn.value() == 0)
    if pressed and not was_pressed and not buz.busy():
        buz.series(3, 100)           # натиск → три біпи на помилку
    was_pressed = pressed

    buz.update()                     # єдиний обов'язок: смикати щоцикл
    # ...тут будь-яка інша логіка, вона не блокована
