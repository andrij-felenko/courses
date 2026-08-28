# Драйвер DC-мотора через H-міст (тип TB6612/DRV8833): два ШІМ-входи на мотор.
# speed: -255..+255 (знак = напрямок, модуль = шпаруватість).
# Raspberry Pi, апаратний ШІМ на двох ніжках через gpiozero.
from gpiozero import PWMOutputDevice

in1 = PWMOutputDevice(17, frequency=20000)  # ШІМ на вході IN1
in2 = PWMOutputDevice(18, frequency=20000)  # ШІМ на вході IN2

def motor_drive(speed):
    speed = max(-255, min(255, speed))      # обрізаємо до діапазону
    duty = abs(speed) / 255                 # модуль = шпаруватість (0..1)

    if speed > 0:                           # уперед: ШІМ на IN1, IN2 мовчить
        in1.value = duty
        in2.value = 0.0
    elif speed < 0:                         # назад: навпаки
        in1.value = 0.0
        in2.value = duty
    else:                                   # 0 → вибіг (обидва входи в нулі)
        in1.value = 0.0
        in2.value = 0.0

def motor_brake():                          # різке гальмо: обидва входи високі
    in1.value = 1.0                         # → мотор закорочено всередині моста
    in2.value = 1.0
