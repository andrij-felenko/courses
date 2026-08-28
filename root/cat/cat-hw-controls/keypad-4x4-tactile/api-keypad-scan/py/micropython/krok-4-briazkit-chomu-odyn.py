import time

DEBOUNCE_MS = 30        # скільки чекати, поки стан устоявся (типово 20..50)

last_stable = 0                 # остання «устояна» карта натисків
last_change_ms = [0] * 16       # коли востаннє змінилася кожна клавіша

# Опитати клавіатуру з антибрязкотом. Повертає символ нового натиску або None.
def keypad_read():
    global last_stable
    now_bits = keypad_scan_raw()        # сирий стан усіх 16 кнопок
    t = time.ticks_ms()
    key = None

    for i in range(16):
        mask = 1 << i
        now_down = now_bits   & mask    # зараз натиснута?
        was_down = last_stable & mask   # була натиснута в устояному стані?

        if bool(now_down) != bool(was_down):    # стан клавіші змінився
            if time.ticks_diff(t, last_change_ms[i]) >= DEBOUNCE_MS:
                # зміна протрималась досить довго — вважаємо її СПРАВЖНЬОЮ
                last_change_ms[i] = t
                if now_down:            # саме натиснення (не відпускання)
                    key = keypad_char(i // 4, i % 4)    # row = i//4, col = i%4
                # оновлюємо устояний біт цієї клавіші
                if now_down:
                    last_stable |=  mask
                else:
                    last_stable &= ~mask
            # якщо не витримало паузу — це брязкіт, ігноруємо (устояний стан не чіпаємо)
    return key
