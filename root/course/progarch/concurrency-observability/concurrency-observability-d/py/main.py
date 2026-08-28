# Наївно: надіслати, дочекатися, тоді надіслати наступний.
# Якщо система завмерла — ми просто НЕ шлемо проби, що мали б бути повільними.
for _ in range(n):
    t0 = perf_counter()
    do_request()                  # затик тут спиняє й сам вимірювальний цикл
    record(perf_counter() - t0)   # у вибірці лише те, що встигли надіслати

# Правильно: у проб є ГРАФІК. Затримку рахуємо від planned-часу,
# а не від миті, коли черга нарешті до неї дійшла.
interval = 1 / rps
start = perf_counter()
for i in range(n):
    planned = start + i * interval
    do_request()
    record(perf_counter() - planned)  # включає й чекання проби в затику
