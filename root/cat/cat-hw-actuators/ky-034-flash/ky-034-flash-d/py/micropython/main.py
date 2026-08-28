from machine import Pin
from time import sleep_ms

led = Pin(5, Pin.OUT)             # S модуля на цифровому виході (ESP32: GPIO5)

for _ in range(3):
    led.value(1)                  # подаємо живлення — модуль світиться (свій колір)
    sleep_ms(500)
    led.value(0)                  # прибираємо живлення — модуль згас
    sleep_ms(500)
# далі нічого: блимнули тричі й затихли
