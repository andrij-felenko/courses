Q   = const(15)
RND = const(1 << (15 - 1))            # 0.5 молодшого розряду — для округлення

# затиск значення у діапазон int16 (насичення замість загортання)
@micropython.viper
def sat16(v: int) -> int:
    if v >  32767: return  32767
    if v < -32768: return -32768
    return v

# один вихідний відлік КІХ на 3 відводи; b[] і x[] — у Q15
def fir3_q15(b, x):
    acc = 0                           # широкий акумулятор: MicroPython-ціле не переповниться
    for k in range(3):
        acc += b[k] * x[k]            # Q15 × Q15 = Q30, копимо в Q30
    acc = (acc + RND) >> Q            # округлюємо й вертаємо Q30 → Q15
    return sat16(acc)                 # звужуємо в 16 біт із насиченням
