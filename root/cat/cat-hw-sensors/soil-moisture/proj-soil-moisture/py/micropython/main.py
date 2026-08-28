import time
from machine import ADC

soil = ADC(0)                       # AO на аналоговому вході

def median9():
    a = []
    for _ in range(9):              # набрали 9 відліків
        a.append(soil.read())
        time.sleep_ms(2)            # коротка пауза між читаннями АЦП
    a.sort()                        # відсортували 9 елементів
    return a[4]                     # середнє за порядком число з 9
