# HC-SR04-подібний модуль: trigger і echo на двох виводах.
# повертає відстань у см або -1, якщо відлуння не прийшло.
from machine import Pin
import time

def ping_blocking(trig_pin, echo_pin):
    trig = Pin(trig_pin, Pin.OUT)
    echo = Pin(echo_pin, Pin.IN)

    # 1) короткий імпульс «пни» — 10 мкс
    trig.low();  time.sleep_us(2)
    trig.high(); time.sleep_us(10)
    trig.low()

    # 2) чекаємо фронт echo (з тайм-аутом, щоб не зависнути назавжди)
    t0 = time.ticks_us()
    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), t0) > 30000:
            return -1.0                       # давач не відповів

    # 3) міряємо ширину імпульсу echo
    start = time.ticks_us()
    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), start) > 25000:
            return -1.0                       # ціль поза діапазоном

    dt = time.ticks_diff(time.ticks_us(), start)  # повний час польоту, мкс
    return dt / 58.0                          # см  (правило: см ≈ мкс / 58)
