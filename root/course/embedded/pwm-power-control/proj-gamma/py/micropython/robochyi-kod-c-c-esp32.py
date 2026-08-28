import math

GAMMA    = 2.2
PWM_BITS = 12
MAX_DUTY = (1 << PWM_BITS) - 1  # 4095

# Для розуміння: формула одного значення
def gamma_runtime(level):
    return round((level / 255.0) ** GAMMA * MAX_DUTY)

# Таблиця: 12 біт ≤ 4095, влазить у звичайний int Python;
# 256 готових значень, порахованих один раз.
gamma_lut = [gamma_runtime(i) for i in range(256)]  # рахуємо ОДИН раз
