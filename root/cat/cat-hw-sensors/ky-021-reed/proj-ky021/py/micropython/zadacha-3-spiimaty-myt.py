from machine import Pin
import time

PIN_REED    = 5
DEBOUNCE_MS = 20                  # двері — не поспішають, вікно можна більше

reed = Pin(PIN_REED, Pin.IN)

def magnet_present(pin: Pin) -> bool:
    return pin.value() == 0

door_closed = magnet_present(reed)  # початковий стан при вмиканні
reading     = door_closed           # останнє миттєве читання
last_change = 0

while True:
    now = time.ticks_ms()
    now_reading = magnet_present(reed)

    # щойно миттєве читання відрізнилось від попереднього — перезапускаємо таймер
    if now_reading != reading:
        reading = now_reading
        last_change = now

    # читання протрималось незмінним довше за вікно → це справжня зміна, не брязкіт
    if time.ticks_diff(now, last_change) >= DEBOUNCE_MS and now_reading != door_closed:
        door_closed = now_reading         # фіксуємо новий стійкий стан
        print("зачинено" if door_closed else "відчинено")
        # сюди — одноразова дія на перехід (надіслати, приспати, увімкнути…)
