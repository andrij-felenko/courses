from machine import Pin, PWM
from time import sleep_ms

PIN = 5
led = PWM(Pin(PIN), freq=5000)  # LUT побудовано вище, в setup-фазі модуля

while True:
    # дихання: 0→255→0
    for level in range(256):
        # duty_u16 бере 0..65535; наш 12-бітний LUT масштабуємо зсувом <<4
        led.duty_u16(gamma_lut[level] << 4)  # ЛИШЕ індексація, жодного float
        sleep_ms(8)
    for level in range(255, -1, -1):
        led.duty_u16(gamma_lut[level] << 4)
        sleep_ms(8)
