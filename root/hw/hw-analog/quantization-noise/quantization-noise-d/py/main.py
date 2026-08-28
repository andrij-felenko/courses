import math

# --- шум квантування 12-бітного АЦП ---
N   = 12
Vfs = 3.3
q       = Vfs / (1 << N)          # крок: 3.3/4096 ≈ 0.806 мВ
e_quant = q / math.sqrt(12.0)     # q/√12 ≈ 0.233 мВ rms

# --- тепловий шум опору давача √(4kTRB) ---
k, T, R, B = 1.38e-23, 300.0, 10000.0, 20000.0
e_therm = math.sqrt(4.0 * k * T * R * B)   # ≈ 1.82 мкВ rms

# --- складаємо незалежні шуми коренем із суми квадратів ---
e_total = math.hypot(e_quant, e_therm)

print(f"шум квантування = {e_quant * 1e3:.3f} мВ rms")   # 0.233
print(f"тепловий шум    = {e_therm * 1e3:.4f} мВ rms")   # 0.0018
print(f"разом           = {e_total * 1e3:.3f} мВ rms")   # ≈ 0.233
