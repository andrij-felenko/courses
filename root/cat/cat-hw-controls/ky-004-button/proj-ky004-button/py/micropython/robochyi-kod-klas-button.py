from machine import Pin
from button import Button

btn = Button(2)                    # сигнал KY-004 на GPIO2; вікно 15 мс, довгий 800 мс — за замовчуванням
led = Pin(13, Pin.OUT)
led_on = False
presses = 0

btn.begin()                        # тут визначиться полярність — не тримай кнопку!

while True:
    btn.update()                   # єдиний обов'язок: смикати часто й неблокуюче

    if btn.pressed():              # мить натиску — рівно раз на тик
        led_on = not led_on
        led.value(led_on)
        presses += 1
    if btn.long_press():           # тримали довше 800 мс
        led_on = False
        led.value(0)
        print("натисків:", presses)

    # ... тут може бути будь-що інше: цикл не блокується кнопкою ...
