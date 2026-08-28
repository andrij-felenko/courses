import math

def g_model(L, T):
    return 4 * math.pi**2 * L / T**2

# --- входи та їхні стандартні невизначеності ---
L, u_L   = 0.9500, 0.0006          # довжина, м (тип B: рулетка ±1 мм)
t50, u_t50 = 97.77, 0.25           # час 50 коливань, с (тип A)
T, u_T   = t50 / 50, u_t50 / 50    # період і його невизначеність
g = g_model(L, T)

# --- коефіцієнти чутливості: аналітично і чисельно (мають збігтися) ---
cL_an, cT_an = g / L, -2 * g / T
h = 1e-7
cL_num = (g_model(L + h, T) - g_model(L - h, T)) / (2 * h)   # ∂g/∂L
cT_num = (g_model(L, T + h) - g_model(L, T - h)) / (2 * h)   # ∂g/∂T

# --- внески у невизначеність g і незалежне складання по квадрату ---
aL, aT = abs(cL_an) * u_L, abs(cT_an) * u_T
u_g = math.hypot(aL, aT)                       # √(aL² + aT²)

print(f"g   = {g:.4f} м/с²")
print(f"c_L: аналітично {cL_an:.3f}, чисельно {cL_num:.3f}")
print(f"c_T: аналітично {cT_an:.3f}, чисельно {cT_num:.3f}")
print(f"внесок L = {aL:.4f}   внесок T = {aT:.4f}")
print(f"u(g) = {u_g:.4f}  →  U = {2*u_g:.2f} (k=2)")

# --- а якби входи КОРЕЛЮВАЛИ з коефіцієнтом r (той самий доданок 2·aL·aT·r) ---
for r in (-1.0, 0.0, 1.0):
    uc = math.sqrt(aL**2 + aT**2 + 2 * aL * aT * r)
    print(f"  r = {r:+.0f}  →  u_c = {uc:.4f}")
