from machine import Pin, Timer

gate = Pin(15, Pin.OUT)           # затвор симістора
tmr = Timer(0)

# по таймеру — короткий імпульс на затвор симістора:
def on_timer(t):                  # спливла затримка d — «час стріляти»
    gate.on()                     # імпульс ~100 мкс защіпає симістор
    time.sleep_us(100)
    gate.off()

# На кожному імпульсі детектора нуля — старт таймера на d:
def on_zero_cross(pin):           # переривання від детектора нуля
    tmr.init(mode=Timer.ONE_SHOT, period=5, callback=on_timer)  # 5.0 мс

zc = Pin(14, Pin.IN)              # детектор нуля
zc.irq(trigger=Pin.IRQ_RISING, handler=on_zero_cross)
