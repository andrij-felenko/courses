# Кожен davach_*() читає регістр стану давача через I2C/SPI,
# обробляє подію й СКИДАЄ прапорець у самому давачі —
# тільки після цього той відпускає лінію IRQ.

from machine import Pin

irq = Pin(2, Pin.IN, Pin.PULL_UP)   # ніжка МК зі спільною лінією (активна в 0)

def obrobnyk_irq(_pin=None):
    # Поки лінію хтось тримає внизу — на ній ще є непочате прохання.
    while irq.value() == 0:
        # Порядок опитування = пріоритет джерел.
        if davach_ruhu_prosyt():
            obsluhy_ruh()          # найважливіший
        elif godynnyk_prosyt():
            obsluhy_godynnyk()
        elif knopka_prosyt():
            obsluhy_knopku()
        else:
            break                  # ніхто не зізнається — уникаємо вічного циклу
