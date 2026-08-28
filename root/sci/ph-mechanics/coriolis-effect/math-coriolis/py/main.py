import math

def cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])
def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def mag(a):
    return math.sqrt(dot(a, a))

Omega = 7.29e-5                      # темп обертання Землі, рад/с
phi   = math.radians(50)            # широта

# вісь Землі (z — угору) і горизонтальна швидкість тіла в площині горизонту
w = (0.0, 0.0, Omega)              # ω уздовж осі
v = (300.0, 0.0, 0.0)             # v_об = 300 м/с у горизонтальній площині

Fc = tuple(-2*c for c in cross(w, v))          # F_Коріоліса / m = −2 ω×v

print("робота (F·v):", round(dot(Fc, v), 12))   # → 0.0 — сила не працює
theta = math.acos(dot(w, v)/(mag(w)*mag(v)))     # кут між ω і v = 90°
print("|F|/m прямо  :", round(mag(Fc), 8))
print("|F|/m формула:", round(2*Omega*mag(v)*math.sin(theta), 8))  # 2Ω v sinθ — те саме

f = 2*Omega*math.sin(phi)                        # параметр Коріоліса
print("f·v (бічне a):", round(f*mag(v), 8))      # горизонтальне відхилення горизонт. руху
