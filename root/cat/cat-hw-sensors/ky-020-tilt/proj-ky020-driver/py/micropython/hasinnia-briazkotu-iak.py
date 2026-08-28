from machine import Pin
import time

TILT   = 2
SETTLE = 30                         # мс: скільки рівень має протриматися, щоб повірити

tilt = Pin(TILT, Pin.IN, Pin.PULL_UP)

last_raw        = 1                 # попереднє СИРЕ читання (1 = рівно)
stable_state    = 1                 # усталений, «прийнятий» стан
last_change_ms  = 0                 # коли сире читання востаннє смикнулось
tilt_count      = 0                 # лічильник СПРАВЖНІХ нахилів

last_raw = stable_state = tilt.value()

# Повертає True рівно в ту ітерацію, коли усталений стан перейшов у «нахил».
def tilt_edge():
    global last_raw, stable_state, last_change_ms
    raw = tilt.value()
    if raw != last_raw:                     # сире читання щойно смикнулось —
        last_change_ms = time.ticks_ms()    # перезапускаємо відлік «тиші»
        last_raw = raw
    # рівень протримався сталим довше за SETTLE і відрізняється від прийнятого?
    if time.ticks_diff(time.ticks_ms(), last_change_ms) > SETTLE and raw != stable_state:
        stable_state = raw                  # приймаємо новий усталений стан
        return stable_state == 0            # True, лише якщо перейшли САМЕ в нахил
    return False

while True:
    if tilt_edge():
        tilt_count += 1
        print("нахилів:", tilt_count)
    # тут може крутитися решта програми — tilt_edge() нічого не блокує
