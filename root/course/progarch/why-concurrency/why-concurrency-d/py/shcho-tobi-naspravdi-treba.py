# I/O-bound: секунда сну = чекання на мережу; time.sleep відпускає GIL.
# Два потоки на одному ядрі перекриваються — конкурентність без паралелізму.
import threading, time

def wait_device():
    time.sleep(1)                       # «чекаємо на пристрій»

t0 = time.perf_counter()
ts = [threading.Thread(target=wait_device) for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
print(time.perf_counter() - t0)         # ≈ 1s, а не 2s: чекання перекрилось
