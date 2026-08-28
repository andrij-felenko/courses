from machine import Pin

btn = Pin(2, Pin.IN)             # підтяжка вже на платі — просто IN, без PULL
led = Pin(25, Pin.OUT)           # вбудований світлодіод

while True:
    if btn.value() == 1:         # pull-down: натиск = «1»
        led.on()
    else:
        led.off()
