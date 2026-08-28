THR_MIN = 0.0
THR_MAX = 1.0

# затиснути команди моторів, зберігши напрямок сумарного моменту
def saturate_preserve(motor) -> None:
    hi = lo = motor[0]
    for i in range(1, N_MOTORS):
        if motor[i] > hi: hi = motor[i]
        if motor[i] < lo: lo = motor[i]
    # якщо розмах вилазить за [MIN,MAX] — стиснути всі до одного масштабу
    span = hi - lo
    room = THR_MAX - THR_MIN
    if span > room and span > 1e-6:
        scale = room / span
        for i in range(N_MOTORS):
            motor[i] = (motor[i] - lo) * scale + THR_MIN
    else:
        # просто підняти/опустити в діапазон, не міняючи різниць
        shift = 0.0
        if lo < THR_MIN: shift = THR_MIN - lo
        elif hi > THR_MAX: shift = THR_MAX - hi
        for i in range(N_MOTORS):
            motor[i] += shift
