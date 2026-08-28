import threading

# Спільний лічильник: його бачать УСІ потоки, що обробляють запити.
g_requests = 0
g_lock = threading.Lock()

def handle_request(path):
    route(path)                 # ← видно у ФУНКЦІЙНІЙ в'ю: що викликає що

    with g_lock:                # ← видно у КОНКУРЕНТНІЙ в'ю: точка синхронізації
        global g_requests
        g_requests += 1         #    спільний ресурс під замком
