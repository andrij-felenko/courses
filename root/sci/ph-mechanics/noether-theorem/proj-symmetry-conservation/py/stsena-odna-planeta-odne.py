import numpy as np

mu = 1.0                          # G·M (нормовані одиниці)
q0 = np.array([0.4, 0.0])         # старт у перигелії
v0 = np.array([0.0, 2.0])         # a=1, e=0.6 → E=−0.5, L=0.8, T=2π

def accel(q):
    r = np.hypot(*q)
    return -mu * q / r**3

def energy(q, v):
    return 0.5 * v @ v - mu / np.hypot(*q)

def ang_mom(q, v):
    return q[0]*v[1] - q[1]*v[0]   # = r²·θ̇  (m = 1)
