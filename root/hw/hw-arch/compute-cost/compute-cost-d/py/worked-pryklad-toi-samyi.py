# Порівняння float32 vs int8 одного детектора на одноплатнику з прискорювачем.
# Міряємо РЕАЛЬНИЙ настінний час інференсу через time.perf_counter.
import time

def bench(interpreter, frame):
    interpreter.set_tensor(input_index, frame)
    t0 = time.perf_counter()
    interpreter.invoke()                          # один прогін детектора
    return (time.perf_counter() - t0) * 1000.0    # мс на кадр

# очікувані порядки для легкого детектора:
#   float32: розмір ~ 7 МБ, інференс ~ 60 мс/кадр (~16 fps), mAP = базова
#   int8   : розмір ~ 1.8 МБ, інференс ~ 12 мс/кадр (~80 fps), mAP −1..2%
