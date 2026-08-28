import time

# кожна задача — [період (мс), мітка «востаннє», що робити]
tasks = [
    [500,  0, toggle_led],   # блимати
    [100,  0, read_sensor],  # опитати давач
    [1000, 0, update_lcd],   # оновити екран
]

while True:
    now = time.ticks_ms()
    for t in tasks:
        if time.ticks_diff(now, t[1]) >= t[0]:
            t[1] = time.ticks_add(t[1], t[0])
            t[2]()               # запускаємо дозрілу задачу
