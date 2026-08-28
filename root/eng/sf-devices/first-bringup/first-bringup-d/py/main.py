from machine import Pin
import time

LED_GPIO = 2                         # світлодіод на платі (звір із розводкою!)

led = Pin(LED_GPIO, Pin.OUT)         # вивід одразу у відомий стан — вихід

while True:                          # "серцебиття": видимий пульс життя
    led.value(1)                     # світлодіод увімкнено
    time.sleep_ms(500)               # пауза 500 мс
    led.value(0)                     # світлодіод вимкнено
    time.sleep_ms(500)               # пауза 500 мс
