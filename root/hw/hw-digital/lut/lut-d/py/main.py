import math

N = 256                                       # вузлів на повний оберт 2π
SIN_LUT = [0.0] * N                            # 256 значень у пам'яті

# один раз на старті: порахувати дорогий math.sin() наперед
def sin_lut_init():
    for i in range(N):
        SIN_LUT[i] = math.sin(2.0 * math.pi * i / N)

# гарячий шлях: жодного math.sin() — лише читання + одне множення
def sin_fast(rad):
    x = rad * (N / (2.0 * math.pi))            # радіани → позиція в таблиці
    i = int(x)                                 # лівий вузол
    f = x - i                                  # дробова частина: 0..1
    a = SIN_LUT[i & (N - 1)]                   # & (N-1): дешеве "mod 256"
    b = SIN_LUT[(i + 1) & (N - 1)]             # правий вузол
    return a + (b - a) * f                     # пряма між a і b
