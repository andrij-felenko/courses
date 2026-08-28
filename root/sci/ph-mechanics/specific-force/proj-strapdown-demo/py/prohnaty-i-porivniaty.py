R, V = 100.0, 20.0                    # радіус і швидкість віражу
OM   = V / R                          # 0.20 рад/с — стала кутова швидкість
G    = 9.81
DT   = 1.0 / 500                      # 500 Гц — типова частота IMU

GYRO = (0.0, 0.0, OM)                 # ← стала (виведено вище)
ACC  = (0.0, OM*OM*R, G)              # ← стала: (0, 4.00, 9.81)

def truth(t):                         # де апарат насправді, у кожну мить
    return (R*math.cos(OM*t), R*math.sin(OM*t), 0.0)

def start():                          # орієнтація на θ=0: курс +90° (ніс на +Y)
    q = qunit((math.cos(math.pi/4), 0.0, 0.0, math.sin(math.pi/4)))
    return q, (0.0, V, 0.0), (R, 0.0, 0.0)

def run(seconds):
    q, v, p = start()
    fw = qrot(q, ACC)                 # засіяти «минуле» прискорення з початку
    a_prev = (fw[0], fw[1], fw[2] - G)
    worst = 0.0
    for k in range(round(seconds / DT)):
        q, v, p, a_prev = strapdown_step(q, v, p, a_prev, GYRO, ACC, DT)
        true = truth(DT * (k + 1))
        worst = max(worst, math.dist(p, true))
    return worst, math.dist(p, (R, 0.0, 0.0))   # (найгірша похибка, незамикання)
