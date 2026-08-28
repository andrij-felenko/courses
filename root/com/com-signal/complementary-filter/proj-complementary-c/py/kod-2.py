import math


def comp_step(c, gx, gy, ax, ay, az, dt):
    # 1. опорні кути з акселерометра (atan2 — стійкий у всіх чвертях)
    roll_acc  = math.atan2(ay, az)
    pitch_acc = math.atan2(-ax, math.sqrt(ay*ay + az*az))

    # 2. засіяти стартову оцінку показом акселерометра, не нулем
    if not c.seeded:
        c.roll  = roll_acc
        c.pitch = pitch_acc
        c.seeded = True
        return                  # перший такт лише сіє, не інтегрує

    # 3. вимикач довіри: якщо |a| далеко від g — підняти alpha майже до 1
    amag = math.sqrt(ax*ax + ay*ay + az*az)
    a = c.alpha
    if abs(amag - c.g) > c.acc_band:
        a = 0.999               # маневр: майже самий гіроскоп

    # 4. зважена сума окремо по кожній осі, кожна — своя вісь гіроскопа
    c.roll  = a * (c.roll  + gx * dt) + (1.0 - a) * roll_acc
    c.pitch = a * (c.pitch + gy * dt) + (1.0 - a) * pitch_acc
