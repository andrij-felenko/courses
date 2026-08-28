# Той самий рейтіометричний перерахунок на MicroPython.
# machine.ADC читає рейтіометрично — код уже є часткою від напруги живлення,
# тож Vж/Vref у математику не входить: працюємо прямо у відношеннях.
from machine import ADC, Pin

ADC_FULL_SCALE = 4096      # 2^12
R_SERIES_OHMS  = 10000.0   # постійний резистор плеча

adc = ADC(Pin(34))         # давач у нижньому плечі дільника

def thermistor_ohms(code):
    # Захист від ділення на нуль на самому краю шкали.
    if code == 0 or code >= ADC_FULL_SCALE:
        return 0.0             # давач закорочений або обірваний
    # R_дав = R · code / (FS − code)  — чисте відношення, без вольтів.
    return R_SERIES_OHMS * code / (ADC_FULL_SCALE - code)

r = thermistor_ohms(adc.read_u16() >> 4)   # 16-бітний відлік → 12 біт
