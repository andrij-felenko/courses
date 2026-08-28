import queue, threading, time

q = queue.Queue()          # черга відліків давача
bus_lock = threading.Lock()  # замок на спільну шину дисплея

def task_sensor():                          # ВИРОБНИК
    while True:
        v = read_sensor()
        q.put(v)                            # безпечно передали відлік (копія)
        time.sleep(0.1)

def task_log():                             # СПОЖИВАЧ
    while True:
        v = q.get()                         # чекаємо й беремо (блок)
        with bus_lock:                      # ← зайняли спільну шину
            write_to_display(v)             #   працюємо з нею
                                            # ← замок звільнено на виході з with
