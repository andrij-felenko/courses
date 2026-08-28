PWM_TOP     =   500          # рівні шпаруватості 0..500 (~9 біт)
IN_MAX      = 65535          # повний розмах 16-бітного входу
STATE_CLAMP = 4 * IN_MAX     # страхувальна межа для станів похибки

def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)

# Простий і швидкий генератор псевдовипадкового для дрожу (xorshift).
def dither_step():
    s = dither_step.s                    # будь-яке ненульове зерно
    s ^= (s << 13) & 0xFFFFFFFF
    s ^= s >> 17
    s ^= (s << 5) & 0xFFFFFFFF
    dither_step.s = s
    # трикутний дрож амплітудою ~один крок квантування (IN_MAX/PWM_TOP):
    step = IN_MAX // PWM_TOP              # розмір одного вихідного рівня у масштабі входу
    a = (s & 0xFFFF) - 32768             # рівномірний -32768..32767
    b = ((s >> 16) & 0xFFFF) - 32768
    return ((a + b) * step) // 65536     # сума двох рівномірних = трикутний, масштабований під крок

dither_step.s = 0x1234567

# Головна функція: один звуковий відлік -> код шпаруватості 0..PWM_TOP.
# Викликати з обробника переривання таймера на частоті вибірки.
def shape2_isr(sample):
    # 1) поправка входу зворотним зв'язком: 2*e1 - e2  =  (1 - z^-1)^2
    u = sample + 2 * shape2_isr.e1 - shape2_isr.e2

    # 2) дрож перед квантуванням — розбиває холості тони й лінеаризує квантувач
    ud = u + dither_step()

    # 3) квантування з округленням до найближчого рівня
    level = (ud * PWM_TOP + IN_MAX // 2) // IN_MAX
    level = clamp(level, 0, PWM_TOP)     # насичення виходу

    # 4) похибку міряємо БЕЗ дрожу (дрож — не помилка, його повертати не треба):
    #    те, що реально віддали цим рівнем, назад у масштаб входу
    y = (level * IN_MAX + PWM_TOP // 2) // PWM_TOP
    e = u - y

    # 5) зсув і страхувальне обмеження станів (проти розгойдування)
    shape2_isr.e2 = clamp(shape2_isr.e1, -STATE_CLAMP, STATE_CLAMP)
    shape2_isr.e1 = clamp(e,             -STATE_CLAMP, STATE_CLAMP)

    return level

shape2_isr.e1 = shape2_isr.e2 = 0
