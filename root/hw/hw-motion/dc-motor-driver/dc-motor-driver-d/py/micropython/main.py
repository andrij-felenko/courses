# Драйвер DC-мотора через H-міст (тип TB6612/DRV8833): два ШІМ-входи на мотор.
# speed: -255..+255 (знак = напрямок, модуль = шпаруватість).
from machine import Pin, PWM

in1 = PWM(Pin(0), freq=20000)              # апаратний ШІМ на вході IN1
in2 = PWM(Pin(1), freq=20000)             # апаратний ШІМ на вході IN2

def _duty(x):                              # 0..255 → 16-бітна шпаруватість
    return (x * 65535) // 255

def motor_drive(speed):
    speed = max(-255, min(255, speed))     # обрізаємо до діапазону
    duty = abs(speed)                      # модуль = шпаруватість

    if speed > 0:                          # уперед: ШІМ на IN1, IN2 мовчить
        in1.duty_u16(_duty(duty))
        in2.duty_u16(0)
    elif speed < 0:                        # назад: навпаки
        in1.duty_u16(0)
        in2.duty_u16(_duty(duty))
    else:                                  # 0 → вибіг (обидва входи в нулі)
        in1.duty_u16(0)
        in2.duty_u16(0)

def motor_brake():                         # різке гальмо: обидва входи високі
    in1.duty_u16(65535)                    # → мотор закорочено всередині моста
    in2.duty_u16(65535)
