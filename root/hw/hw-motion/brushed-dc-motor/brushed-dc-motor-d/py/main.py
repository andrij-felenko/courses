# MicroPython: та сама рампа шпаруватості на апаратному ШІМ.
from machine import Pin, PWM
from time import sleep_ms

motor = PWM(Pin(MOTOR_PWM), freq=20_000)   # 20 кГц — вище чутності

# duty_u16: 0..65535. Нарощуємо шпаруватість до target_u16 плавно.
for duty in range(0, target_u16, 256):
    motor.duty_u16(duty)   # середня напруга росте плавно
    sleep_ms(8)            # ~даємо ротору розкрутитися й підняти проти-ЕРС
