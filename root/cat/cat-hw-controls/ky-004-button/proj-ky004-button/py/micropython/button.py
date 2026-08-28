# button.py — неблокуюча обгортка кнопки під KY-004 (і будь-яку іншу).
# Сама визначає полярність (спокій на старті), гасить брязкіт,
# віддає події «натиснуто/відпущено» й детектить довгий натиск.
from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms


class Button:
    # pin — номер цифрового виводу із сигналом; debounce_ms — вікно антибрязкоту;
    # long_ms — поріг довгого натиску (0 → детект вимкнено).
    def __init__(self, pin, debounce_ms=15, long_ms=800):
        self._pin_num = pin
        self._debounce = debounce_ms
        self._long = long_ms

    # Викликати один раз на старті. Пін — як IN: підтяжка вже на платі KY-004.
    def begin(self):
        self._pin = Pin(self._pin_num, Pin.IN)
        sleep_ms(2)                       # дати лінії влягтися перед зчитуванням спокою
        self._idle = self._pin.value()    # рівень спокою → еталон «відпущено»
        self._stable = self._idle         # усталений стан стартує зі спокою
        self._reading = self._idle
        self._changed = ticks_ms()
        self._press_start = 0
        self._pressed_now = False
        self._released_now = False
        self._long_now = False
        self._long_fired = False

    # Викликати ЧАСТО (щопрохід циклу). Не блокує. Оновлює стан і зводить події.
    def update(self):
        self._pressed_now = False         # події живуть один прохід
        self._released_now = False
        self._long_now = False
        now = ticks_ms()
        raw = self._pin.value()

        if raw != self._reading:          # сирий рівень смикнувся — почати відлік вікна
            self._reading = raw
            self._changed = now

        # рівень протримався стабільно ціле вікно → визнати його усталеним
        if ticks_diff(now, self._changed) >= self._debounce and raw != self._stable:
            self._stable = raw
            if self._stable != self._idle:   # перейшли зі спокою → НАТИСК
                self._pressed_now = True
                self._press_start = now
                self._long_fired = False
            else:                            # повернулися у спокій → ВІДПУЩЕНО
                self._released_now = True

        # довгий натиск: кнопка усталено натиснута довше за поріг — раз на утримання
        if (self._long and self.is_pressed() and not self._long_fired
                and ticks_diff(now, self._press_start) >= self._long):
            self._long_now = True
            self._long_fired = True

    # ── Питання назовні ────────────────────────────────────────────────
    def is_pressed(self):   return self._stable != self._idle  # усталений стан «натиснуто»
    def pressed(self):      return self._pressed_now           # мить натиску (1 прохід)
    def released(self):     return self._released_now          # мить відпускання
    def long_press(self):   return self._long_now              # щойно перетнули поріг утримання
