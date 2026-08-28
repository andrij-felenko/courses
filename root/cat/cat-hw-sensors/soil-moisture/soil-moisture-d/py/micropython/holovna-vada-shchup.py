from machine import ADC, Pin
from time import sleep_ms, sleep

power = Pin(7, Pin.OUT)          # VCC давача живимо з цифрового виводу
soil = ADC(Pin(34))             # штир AO (вхід АЦП)
soil.atten(ADC.ATTN_11DB)

power.value(0)                   # у спокої давач знеструмлений

def measure():
    power.value(1)               # подали живлення на щуп
    sleep_ms(10)                 # даємо напрузі усталитися
    v = soil.read()              # швидко зняли
    power.value(0)               # одразу знеструмили — щуп «відпочиває»
    return v

while True:
    print(measure())
    sleep(60)                    # міряємо раз на хвилину, а не безперервно
