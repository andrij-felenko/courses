from machine import ADC, Pin
from time import sleep_ms

vrx = ADC(Pin(34))                # VRx на аналоговому вході
DEADZONE = 96                     # напівширина мертвої зони, одиниць АЦП
ADC_MAX = 4095                    # 12-бітний АЦП
center_x = 2048                   # уточнимо нижче


def _map(v, in_lo, in_hi, out_lo, out_hi):
    return (v - in_lo) * (out_hi - out_lo) // (in_hi - in_lo) + out_lo


def calibrate():
    acc = 0
    for _ in range(32):
        acc += vrx.read()
        sleep_ms(4)
    return acc // 32              # справжній центр саме цього екземпляра


def axis(raw, center):
    d = raw - center                          # відхилення від центру
    if -DEADZONE < d < DEADZONE:
        return 0                              # у мертвій зоні — нуль
    # масштабуємо решту ходу (center..крайнє) у зручні −100..+100
    if d > 0:
        return _map(d,  DEADZONE, ADC_MAX - center, 0,  100)
    else:
        return _map(d, -DEADZONE,        -center,   0, -100)


center_x = calibrate()

while True:
    vx = axis(vrx.read(), center_x)           # −100..+100, 0 у спокої
    print(vx)
    sleep_ms(50)
