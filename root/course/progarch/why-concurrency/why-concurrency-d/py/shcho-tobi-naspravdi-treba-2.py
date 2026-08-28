# CPU-bound у Python оголює межу навпіл — через глобальне блокування
# інтерпретатора (GIL): у стандартній збірці два потоки НЕ рахують водночас.
import threading, multiprocessing, time

def crunch():
    s = 0
    for n in range(60_000_000): s += n     # секунда чистої лічби

# ПОТОКИ: GIL пускає до байткоду по одному → виграшу нема
t0 = time.perf_counter()
ts = [threading.Thread(target=crunch) for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
print("потоки:", time.perf_counter() - t0)      # ≈ 2s — конкурентність без паралелізму

# ПРОЦЕСИ: окремі інтерпретатори на окремих ядрах → справжній паралелізм
t0 = time.perf_counter()
ps = [multiprocessing.Process(target=crunch) for _ in range(2)]
for p in ps: p.start()
for p in ps: p.join()
print("процеси:", time.perf_counter() - t0)      # ≈ 1s — аж тепер ядра рахують водночас
