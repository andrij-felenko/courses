import time
from machine import Pin
import onewire, ds18x20

ow = onewire.OneWire(Pin(4))        # спільна лінія DQ шини 1-Wire
sensors = ds18x20.DS18X20(ow)
roms = sensors.scan()               # знайти давачі на шині

while True:
    sensors.convert_temp()          # команда «виміряти» всім давачам
    time.sleep_ms(750)              # чекаємо конверсію (до 750 мс на 12 бітах)

    if not roms:                    # давач не відгукнувся
        print("DS18B20 не на звязку")
    else:
        t = sensors.read_temp(roms[0])   # забрати число з першого, уже в °C
        print("{:.2f} C".format(t))      # дві цифри після коми

    time.sleep_ms(250)
