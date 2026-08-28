from machine import Pin, PWM
import sys

servo = PWM(Pin(18), freq=50)

def write_us(us):
    servo.duty_ns(int(us) * 1000)

write_us(1520)                          # старт від паспортної нейтралі
print("Введи ширину в мкс (напр. 1520) і Enter:")

while True:
    line = sys.stdin.readline().strip() # прочитати рядок із REPL/порту
    if not line:
        continue
    try:
        us = int(line)
    except ValueError:
        continue
    if 1000 <= us <= 2000:              # не пускати за межі ходу
        write_us(us)
        print("->", us, "мкс")
    else:
        print("поза 1000..2000 — пропущено")
