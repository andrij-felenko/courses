import time, statistics, math

def measure(func, make_input, n, trials=5, warmups=2):
    """Медіанний час одного виклику func(make_input(n))."""
    warm = make_input(n)
    for _ in range(warmups):          # прогрів: сторінки, кеш, у JIT-мовах — компіляція
        func(warm)
    samples = []
    for _ in range(trials):
        data = make_input(n)          # свіжий вхід щоразу — не міряємо вже прогрітий кеш
        t0 = time.perf_counter()      # монотонний годинник, роздільність — краще за мкс
        func(data)
        samples.append(time.perf_counter() - t0)
    return statistics.median(samples) # медіана глушить поодинокі сплески ОС/GC

def doubling(func, make_input, n0, steps, **kw):
    """Друкує n, час, відношення T(2n)/T(n) і показник b = log₂(відношення)."""
    print(f"{'n':>9}  {'T (с)':>10}  {'T(2n)/T(n)':>10}  {'b=log₂':>7}")
    prev = None
    n = n0
    for _ in range(steps):
        t = measure(func, make_input, n, **kw)
        if prev is None:
            print(f"{n:>9}  {t:>10.6f}  {'—':>10}  {'—':>7}")
        else:
            r = t / prev
            print(f"{n:>9}  {t:>10.6f}  {r:>10.2f}  {math.log2(r):>7.2f}")
        prev = t
        n *= 2
