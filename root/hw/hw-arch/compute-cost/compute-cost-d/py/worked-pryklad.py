# Профілювання конвеєра бортового зору поетапно.
# time.perf_counter дає настінний час; контекстний менеджер
# міряє етап від входу в `with` до виходу.
import time
from contextlib import contextmanager

@contextmanager
def stage(name):
    t0 = time.perf_counter()
    yield
    dt = (time.perf_counter() - t0) * 1000.0
    print(f"{name:<12} {dt:6.2f} ms")

def process_frame():
    with stage("захоплення"):  f = capture()           # камера → буфер
    with stage("ROI"):         r = select_roi(f)       # звузити ділянку
    with stage("класика"):     preprocess(r)           # поріг/фільтр/підготовка
    with stage("нейромережа"): d = infer(r)            # детектор (CPU або TPU)
    with stage("MAVLink"):     angle = send_cmd(d)     # кут → політний контролер
