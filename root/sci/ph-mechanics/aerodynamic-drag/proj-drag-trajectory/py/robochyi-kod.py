import numpy as np

g   = 9.81            # м/с²
rho = 1.2             # кг/м³, повітря коло землі

def make_accel(m, Cd, A):
    "Прискорення як функція швидкості: a = g − β·|v|·v."
    beta = 0.5*Cd*rho*A / m
    gvec = np.array([0.0, -g])
    def accel(v):
        speed = np.hypot(v[0], v[1])      # |v| — повна швидкість
        return gvec - beta*speed*v        # опір: величина ∝ |v|², напрям −v̂
    return accel

def euler_step(r, v, accel, dt):
    return r + v*dt, v + accel(v)*dt      # найпряміший крок: один нахил

def rk4_step(r, v, accel, dt):
    # стан (r, v); похідні: dr/dt = v, dv/dt = a(v). Опитуємо нахил 4 рази.
    k1r, k1v = v,              accel(v)
    k2r, k2v = v + 0.5*dt*k1v, accel(v + 0.5*dt*k1v)
    k3r, k3v = v + 0.5*dt*k2v, accel(v + 0.5*dt*k2v)
    k4r, k4v = v + dt*k3v,     accel(v + dt*k3v)
    r_new = r + dt/6*(k1r + 2*k2r + 2*k3r + k4r)
    v_new = v + dt/6*(k1v + 2*k2v + 2*k3v + k4v)
    return r_new, v_new
