import time

t0 = time.monotonic()
# ... робота ...
elapsed = time.monotonic() - t0                  # завжди ≥ 0

deadline = time.monotonic() + 30.0
left = max(0.0, deadline - time.monotonic())     # скільки лишилося

stamp = time.time()                              # момент за календарем
print(time.get_clock_info("monotonic"))          # який годинник під сподом
