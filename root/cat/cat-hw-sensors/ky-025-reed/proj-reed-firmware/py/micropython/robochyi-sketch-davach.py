from machine import Pin
import time

REED        = 4                  # D0 давача на GPIO4
LED         = 2                  # «двері відчинені» — індикатор (вбудований LED)
ACTIVE      = 0                  # рівень, коли магніт поруч = двері ЗАЧИНЕНІ: 0 = LOW

DEBOUNCE_MS = 30

reed = Pin(REED, Pin.IN)
led  = Pin(LED, Pin.OUT)

closed     = (reed.value() == ACTIVE)   # початковий стан — як є при старті
was_closed = closed
opens      = 0                   # скільки разів відчиняли
t_edge     = 0

led.value(0 if closed else 1)
print("старт: двері зачинені" if closed else "старт: двері ВІДЧИНЕНІ")

while True:
    now_closed = (reed.value() == ACTIVE)
    now = time.ticks_ms()

    if now_closed != was_closed and time.ticks_diff(now, t_edge) >= DEBOUNCE_MS:
        t_edge = now
        was_closed = now_closed
        closed = now_closed

        if not closed:                  # край «зачинено → відчинено» — це відкривання
            opens += 1
            led.value(1)
            print("ВІДЧИНИЛИ (разів:", opens, ")")
        else:                           # край «відчинено → зачинено»
            led.value(0)
            print("зачинили")
