import math

# Чутливість акселерометра з паспорта: ±2g на 16-бітному АЦП
# → 16384 відліки на 1g.
ACCEL_SCALE = 1.0 / 16384.0   # відлік → частки g

def tilt_from_accel(raw_x, raw_y, raw_z):
    # крок 1: сирі відліки АЦП → частки g
    ax = raw_x * ACCEL_SCALE
    ay = raw_y * ACCEL_SCALE
    az = raw_z * ACCEL_SCALE

    # крок 2: довжина вектора — перевірка, чи давач у спокої
    mag = math.sqrt(ax*ax + ay*ay + az*az)   # у спокої має бути ~1.0 g

    # крок 3: кути нахилу з проєкцій гравітації (радіани → градуси)
    pitch = math.degrees(math.atan2(ax, az))   # тангаж
    roll  = math.degrees(math.atan2(ay, az))   # крен
    # якщо mag помітно відрізняється від 1g — є рух, нахилу зараз вірити не можна
    return pitch, roll, mag
