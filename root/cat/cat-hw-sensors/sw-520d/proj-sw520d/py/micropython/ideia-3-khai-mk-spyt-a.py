from machine import Pin

PIN_SW = 2                             # переносно чіпляємо переривання на будь-який GPIO

shock_flag = False                     # прапорець «була подія»

def isr_shock(pin):                     # обробник: викликається апаратно на фронті
    global shock_flag
    shock_flag = True                   # лише підняти прапорець — і нічого більше

sw = Pin(PIN_SW, Pin.IN, Pin.PULL_UP)
# спадний фронт (HIGH→LOW) = момент замикання кульки
sw.irq(trigger=Pin.IRQ_FALLING, handler=isr_shock)

while True:
    if shock_flag:
        shock_flag = False              # погасити прапорець до наступної події
        print("прокинулись від струсу!")
        # ... тут — реакція: увімкнути, записати, послати сигнал ...
    # ... а тут МК може заснути до наступного переривання ...
