from threading import Thread

# ЛІК: кожен лічильник — в окремому об'єкті → не ділить «лінію» із сусідом
class PaddedCounter:
    def __init__(self):
        self.value = 0

counters = [PaddedCounter() for _ in range(4)]   # тепер кожен — окремо

def worker(core):
    for _ in range(100_000_000):
        counters[core].value += 1          # ядра чіпають РІЗНІ об'єкти — гонки лінії нема
