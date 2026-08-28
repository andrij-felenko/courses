from machine import Pin

# Чотири виводи, на яких висять резистори R, R/2, R/4, R/8.
# pins[0] — наймолодший біт (через найбільший резистор R),
# pins[3] — старший біт (через найменший резистор R/8).
pins = [Pin(n, Pin.OUT) for n in (0, 1, 2, 3)]   # ваги 1, 2, 4, 8

# Виставити 4-бітне значення на ЦАП із зважених резисторів.
def dac_write(value):
    for i, pin in enumerate(pins):
        pin.value((value >> i) & 1)   # біт i → від молодшого до старшого

dac_write(11)   # 1011 → очікуємо рівень коду 11 із 15
while True:
    pass
