from machine import Pin
import time

pg_sensors = Pin('C0', Pin.IN)       # Power-Good шини давачів (вхід)

# Чекати, доки шина підтвердить готовність; не зависати назавжди.
def wait_power_good(pg, timeout_ms):
    deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        if pg.value():                 # шина дійшла номіналу
            return True
        time.sleep_ms(1)
    return False                       # не піднялася — несправність

def power_up_sequence():
    en_sensors.value(1)
    if not wait_power_good(pg_sensors, 50):
        fault_shutdown()               # шина не встала — гасимо все
        return
    en_radio.value(1)
    # ... далі за тією ж схемою
