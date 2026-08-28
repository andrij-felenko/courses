import math

L, C = 100e-6, 100e-12           # Гн, Ф
w0 = 1/math.sqrt(L*C)            # власна частота, рад/с
T  = 2*math.pi/w0                # період, с
q0 = C*5.0                       # заряджаємо конденсатор до 5 В

def energy(q, I):
    "електрична + магнітна, Дж"
    return q*q/(2*C) + L*I*I/2

def step_forward(q, I, dt):      # обидва — зі СТАРОГО стану
    return q - dt*I, I + dt*q/(L*C)

def step_symplectic(q, I, dt):   # струм зі старого q, заряд — з НОВОГО I
    I_new = I + dt*q/(L*C)
    return q - dt*I_new, I_new

def step_verlet(q, I, dt):       # пів кроку струму · крок заряду · пів кроку струму
    I_half = I + (dt/2)*q/(L*C)
    q_new  = q - dt*I_half
    return q_new, I_half + (dt/2)*q_new/(L*C)

def ring(step, periods=10, per_period=200):
    "Проганяє контур і вертає (E_min, E_max, E_кінець) у частках від початкової."
    dt = T/per_period
    q, I = q0, 0.0
    E0 = energy(q, I)
    lo = hi = 1.0
    for _ in range(periods*per_period):
        q, I = step(q, I, dt)
        e = energy(q, I)/E0
        lo, hi = min(lo, e), max(hi, e)
    return lo, hi, energy(q, I)/E0

for name, step in (("явний Ейлер",   step_forward),
                   ("симплектичний", step_symplectic),
                   ("Верле",         step_verlet)):
    print("%-14s E: від %.4f до %.4f, наприкінці %.4f" % ((name,) + ring(step)))
