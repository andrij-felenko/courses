import math

g   = 9.81     # м/с²   прискорення вільного падіння
rho = 1.2      # кг/м³  густина повітря коло землі

def terminal(m, Cd, A):
    "Аналітична межа: там, де опір рівно з'їдає вагу."
    return math.sqrt(2*m*g / (Cd*rho*A))

def fall(m, Cd, A, dt=0.001, t_end=25.0):
    "Крок за кроком інтегруємо m·dv/dt = m·g − ½·Cd·ρ·A·v²."
    beta = 0.5*Cd*rho*A / m         # a = g − beta·v²
    v = 0.0                         # старт зі спокою
    t = 0.0
    while t < t_end:
        a  = g - beta * v*abs(v)    # опір завжди проти руху
        v += a * dt                 # ← увесь метод Ейлера тут
        t += dt
        yield t, v
