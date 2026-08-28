import time, random

n = 1_000_000
data = random.sample(range(10 * n), n)   # мільйон різних чисел

as_list = list(data)                      # звичайний список
as_set  = set(data)                       # гешмножина з тих самих чисел

needle = -1                               # свідомо якого НЕМА — найгірший випадок

t = time.perf_counter()
_ = needle in as_list                     # доведеться пройти всі n елементів
print("список: ", time.perf_counter() - t)   # ~десяті частки секунди

t = time.perf_counter()
_ = needle in as_set                      # h(needle) → одна комірка, і все
print("множина:", time.perf_counter() - t)   # ~мікросекунди
