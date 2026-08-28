# Реверс полярності на ГОЛІЙ пластині (плата LM358 не задіяна).
# Гребінки пластини — на GPIO25 і GPIO26; між GPIO25 і GPIO34 — опорний
# резистор R_ref, сама пластина — між GPIO34 і GPIO26. Читаємо GPIO34 (ADC1).

from machine import ADC, Pin
import time

DRV_A = 25                          # гребінка A + опорний резистор до NODE
DRV_B = 26                          # гребінка B
ADC_FS = 4095                       # повна шкала 12-біт АЦП
node = ADC(Pin(34))                 # середина подільника → ADC1
node.atten(ADC.ATTN_11DB)

PERIOD    = 60000                   # період між вимірами, мс (тут 1 хв)
SETTLE_MS = 30                      # усталення напруги на подільнику
DRY_ENTER = 2600                    # пороги — у нормованих відліках, калібрувати
WET_ENTER = 1500

raining = False
flip = False                        # чергування полярності
last_measure = time.ticks_ms()

# один вимір: подати полярність, усталити, зчитати середину, знеструмити,
# а тоді нормувати так, щоб «менше = мокріше» незалежно від напрямку струму
def measure_once(reversed):
    hi = DRV_B if reversed else DRV_A   # яка гребінка «плюс» цього разу
    lo = DRV_A if reversed else DRV_B
    Pin(hi, Pin.OUT).value(1)
    Pin(lo, Pin.OUT).value(0)
    time.sleep_ms(SETTLE_MS)            # коротке усталення напруги на подільнику
    raw = node.read()
    # знеструмлюємо пластину: обидві ноги у Hi-Z, струм крізь вологу спинено
    Pin(hi, Pin.IN)
    Pin(lo, Pin.IN)
    # при розвороті плечі міняються місцями → відлік інвертується; вирівнюємо
    return (ADC_FS - raw) if reversed else raw

Pin(DRV_A, Pin.IN)                  # старт — пластина знеструмлена (Hi-Z)
Pin(DRV_B, Pin.IN)

while True:
    if time.ticks_diff(time.ticks_ms(), last_measure) >= PERIOD:
        last_measure = time.ticks_ms()
        v = measure_once(flip)          # полярність — по черзі
        flip = not flip

        if not raining and v < WET_ENTER:
            raining = True
        if raining and v > DRY_ENTER:
            raining = False

        print("вологість =", v, "  →", "дощ" if raining else "сухо")
    # весь інший час пластина у Hi-Z, МК вільний
