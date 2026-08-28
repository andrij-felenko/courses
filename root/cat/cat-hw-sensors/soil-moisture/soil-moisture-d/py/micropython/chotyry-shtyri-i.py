from machine import ADC, Pin
from time import sleep_ms

soil = ADC(Pin(34))              # штир AO давача (вхід АЦП)
soil.atten(ADC.ATTN_11DB)        # повний діапазон 0..3.3 В

DRY = 2800                       # сухіше за це — вмикаємо полив
WET = 1800                       # вологіше за це — вимикаємо
watering = False                 # поточний стан насоса

def read_soil():                 # середнє з 8 замірів — глушимо шум
    total = 0
    for _ in range(8):
        total += soil.read()
        sleep_ms(2)
    return total // 8

while True:
    v = read_soil()              # більше = сухіше
    if not watering and v > DRY:
        watering = True          # пересохло → полив
    if watering and v < WET:
        watering = False         # зволожилось → стоп

    print("вологість(АЦП)=", v, "  [полив]" if watering else "  [сухо стоїть]")
    sleep_ms(1000)
