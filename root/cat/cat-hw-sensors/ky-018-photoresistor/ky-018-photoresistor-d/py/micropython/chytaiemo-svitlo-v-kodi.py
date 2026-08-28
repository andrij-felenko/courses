from machine import ADC, Pin      # S давача на аналоговому вході (ESP32: GPIO34)
from time import sleep_ms

ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)          # повний розмах входу, ~0…3.3 В

while True:
    light = ldr.read()            # 0…4095 на 12-бітному АЦП ESP32
    print(light)                  # темно → мале число; світло → близько 4095
    sleep_ms(200)
