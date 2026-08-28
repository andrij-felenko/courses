from machine import Pin, Timer

gate = Pin(15, Pin.OUT)            # затвор ключа (через драйвер)
tmr = Timer(0)

def turn_off(t):                   # сплив час провідності
    gate.off()                     # ЗАКРИТИ ключ — обрізаємо задній фронт

def on_zero_cross(pin):            # переривання від детектора нуля
    gate.on()                      # ВІДКРИТИ ключ одразу — і тримаємо рівень
    tmr.init(mode=Timer.ONE_SHOT, period=5, callback=turn_off)  # 5.0 мс = 50%

zc = Pin(14, Pin.IN)               # детектор нуля
zc.irq(trigger=Pin.IRQ_RISING, handler=on_zero_cross)
