# Давач дощу цілим модулем: імпульсно живимо VCC модуля з GPIO,
# читаємо AO з ADC1 лише під час короткого вікна. БЕЗ реверсу полярності —
# перевертати живлення плати з LM358 не можна.

from machine import ADC, Pin
import time

PWR = Pin(26, Pin.OUT)              # живлення VCC модуля (нога GPIO або ключ на транзисторі)
ao  = ADC(Pin(34))                  # аналоговий вихід модуля → ADC1
ao.atten(ADC.ATTN_11DB)

PERIOD    = 60000                   # період між вимірами, мс (тут 1 хв)
SETTLE_MS = 30                      # усталення LM358 + подільника
DRY_ENTER_MV = 2400
WET_ENTER_MV = 1500

raining = False
last_measure = time.ticks_ms()

# один вимір: подати живлення на весь модуль, усталити, зчитати AO, зняти живлення
def measure_once():
    PWR.value(1)                    # подали живлення на весь модуль
    time.sleep_ms(SETTLE_MS)        # LM358 і подільник усталюються
    mv = ao.read_uv() // 1000
    PWR.value(0)                    # зняли живлення — струму крізь вологу нема
    return mv

PWR.value(0)                        # старт — модуль знеструмлений

while True:
    if time.ticks_diff(time.ticks_ms(), last_measure) >= PERIOD:
        last_measure = time.ticks_ms()
        mv = measure_once()

        if not raining and mv < WET_ENTER_MV:
            raining = True
        if raining and mv > DRY_ENTER_MV:
            raining = False

        print("AO =", mv, "мВ  →", "дощ" if raining else "сухо")
    # весь інший час модуль знеструмлений, МК вільний (тут доречний і сон)
