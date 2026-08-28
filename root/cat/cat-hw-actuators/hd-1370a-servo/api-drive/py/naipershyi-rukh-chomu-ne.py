from machine import Pin, PWM
from time import sleep_ms

# ESP32: будь-який вихідний пін; тут GPIO 18
servo = PWM(Pin(18), freq=50)   # 50 Гц одразу, як і треба серву

def write_us(us):
    servo.duty_ns(int(us) * 1000)   # мкс → нс; duty_ns — прямий аналог writeMicroseconds

write_us(1520)                  # справжня нейтраль HD-1370A
sleep_ms(500)

while True:
    write_us(1520)              # центр
    sleep_ms(1000)
    write_us(1520 + 333)        # ≈ +30° від центру (30° · 11.1 мкс/°)
    sleep_ms(1000)
