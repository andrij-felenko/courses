import time
from machine import Pin

DEBOUNCE_MS = 25

class Button:
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)  # на модулі підтяжки немає!
        self.stable = True                   # спокій = HIGH (відпущено)
        self.last_read = True                # останній миттєвий відлік
        self.last_change = time.ticks_ms()   # коли рівень востаннє змінився, мс
        self.pressed_event = False           # один імпульс у мить натиску

    # Викликати щоцикл. Оновлює стан; pressed_event — один імпульс на натиск.
    def update(self):
        self.pressed_event = False
        now = bool(self.pin.value())         # 1 = відпущено, 0 = натиснуто

        if now != self.last_read:            # рівень смикнувся — перезапустити вікно
            self.last_change = time.ticks_ms()
            self.last_read = now

        # рівень протримався сталим досить довго — приймаємо його
        if time.ticks_diff(time.ticks_ms(), self.last_change) >= DEBOUNCE_MS \
                and now != self.stable:
            self.stable = now
            if not self.stable:              # перехід HIGH→LOW = справжній натиск
                self.pressed_event = True

    def pressed(self):  return self.pressed_event   # один імпульс
    def held(self):     return not self.stable      # тримають зараз
