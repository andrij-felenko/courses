import threading

def gate_pulse_us(us):            # імпульс ~us мкс защіпає симістор
    gate_write(1)
    time.sleep(us / 1_000_000)
    gate_write(0)

def on_timer():                   # спливла затримка d — «час стріляти»
    gate_pulse_us(100)            # імпульс ~100 мкс защіпає симістор

# На кожному імпульсі детектора нуля — старт таймера на d,
# по таймеру — короткий імпульс на затвор симістора:
def on_zero_cross():              # переривання від детектора нуля
    threading.Timer(0.005, on_timer).start()  # 5.0 мс = 5000 мкс
