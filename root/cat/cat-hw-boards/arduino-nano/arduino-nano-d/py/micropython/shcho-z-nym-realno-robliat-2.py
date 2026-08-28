from machine import Pin, ADC, PWM
from time import sleep_ms

btn = Pin(2, Pin.IN, Pin.PULL_UP)   # внутрішня підтяжка: вільний стан = HIGH
pot = ADC(0)                        # A0, середній вивід потенціометра
led = PWM(Pin(9))                   # світлодіод на ШІМ-виводі ~D9

while True:
    pressed = (btn.value() == 0)    # натиснуто = замкнуто на GND
    if pressed:
        raw = pot.read()            # 0..1023 (десятибітний АЦП)
        duty = raw >> 2             # звести до 0..255 для ШІМ
        led.duty(duty)              # яскравість за положенням ручки
    else:
        led.duty(0)                 # відпущено — згасити
    sleep_ms(10)
