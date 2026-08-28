# Пул із N потоків тягне спільну чергу. Тепер водночас
# обробляється N запитів — чекання в черзі падає приблизно в N разів.
WORKERS = 4

def worker_loop(q: "queue.Queue[Request]") -> None:
    while (req := q.get()) is not None:  # безпечний забір із черги
        handle_request(req)              # чотири такі йдуть ОДНОЧАСНО

def serve_all_parallel(q: "queue.Queue[Request]") -> None:
    threads = [threading.Thread(target=worker_loop, args=(q,))
               for _ in range(WORKERS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
