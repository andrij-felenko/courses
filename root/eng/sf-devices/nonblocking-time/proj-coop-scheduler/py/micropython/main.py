import time

# кожна задача — [функція, період_мс, остання_мітка]
tasks = [
    [blink,         500,   0],
    [read_sensor,   1000,  0],
    [send_data,     10000, 0],
    [update_screen, 100,   0],
]

while True:
    now = time.ticks_ms()
    for t in tasks:
        if time.ticks_diff(now, t[2]) >= t[1]:
            t[0]()                              # задача виконується до кінця
            t[2] = time.ticks_add(t[2], t[1])   # рівна сітка, а не = now
