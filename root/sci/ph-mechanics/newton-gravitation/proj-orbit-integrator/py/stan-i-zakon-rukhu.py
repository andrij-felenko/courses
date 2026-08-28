import math

GM = 1.0                          # одиниці, де гравітаційний параметр = 1

def accel(x, y):
    r = math.hypot(x, y)          # відстань до зорі
    k = -GM / r**3                # спільний множник −GM/r³
    return k * x, k * y           # прискорення = −GM·(x, y)/r³, тягне до центра

def energy(x, y, vx, vy):
    return 0.5 * (vx*vx + vy*vy) - GM / math.hypot(x, y)   # ½v² − GM/r
