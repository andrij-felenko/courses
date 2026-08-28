from machine import ADC, Pin
from time import sleep_ms

ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
led = Pin(2, Pin.OUT)             # вбудований світлодіод ESP32
DARK = 1200                       # поріг: нижче — вважаємо «темно» (добери під себе!)

while True:
    light = ldr.read()
    dark = light < DARK           # менше світла = менший відлік
    led.value(1 if dark else 0)
    sleep_ms(100)
