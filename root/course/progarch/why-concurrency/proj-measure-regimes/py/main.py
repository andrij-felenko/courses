import threading, multiprocessing, time, sys

# ── Одиниця роботи ─────────────────────────────────────────────────────
def io_one():
    time.sleep(1)                  # чесний замінник мережі: time.sleep ВІДПУСКАЄ GIL

_blackhole = 0
def cpu_one():
    s = 0
    for n in range(60_000_000):    # N підбери, щоб одна задача важила ~1 с
        s += n
    global _blackhole
    _blackhole ^= s                # щоб «непотрібний» цикл ніхто не викинув

# ── Режими ─────────────────────────────────────────────────────────────
def sequential(task):
    task(); task()                 # одна за одною → нуль відліку

def with_threads(task):            # конкурентність; для CPU впирається в GIL
    ts = [threading.Thread(target=task) for _ in range(2)]
    for t in ts: t.start()
    for t in ts: t.join()

def with_processes(task):          # окремі інтерпретатори → окремі GIL → реальні ядра
    ps = [multiprocessing.Process(target=task) for _ in range(2)]
    for p in ps: p.start()
    for p in ps: p.join()

# ── Секундомір: розігрів + мінімум із кількох прогонів ─────────────────
def _once(run):
    t0 = time.perf_counter()
    run()
    return time.perf_counter() - t0

def timeit(label, run):
    run()                          # РОЗІГРІВ — перший прогін не міряємо
    best = min(_once(run) for _ in range(3))
    print(f"{label:<30} {best:.2f}s")

def main():
    print("GIL увімкнено:", getattr(sys, "_is_gil_enabled", lambda: True)())
    print("ядер:", multiprocessing.cpu_count())

    timeit("I/O · послідовно",     lambda: sequential(io_one))       # ≈ 2.00s
    timeit("I/O · потоки",         lambda: with_threads(io_one))     # ≈ 1.00s
    timeit("CPU · послідовно",     lambda: sequential(cpu_one))      # ≈ 2.00s
    timeit("CPU · потоки (GIL!)",  lambda: with_threads(cpu_one))    # ≈ 2.00s
    timeit("CPU · процеси",        lambda: with_processes(cpu_one))  # ≈ 1.00s

# spawn/forkserver РЕ-ІМПОРТУють цей модуль у дитині — без цієї огорожі
# кожен нащадок знову побіг би у main() і породив нескінченну лавину.
if __name__ == "__main__":
    main()
