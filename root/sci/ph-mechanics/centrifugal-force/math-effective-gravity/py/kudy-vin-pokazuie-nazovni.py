import math

def cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])

Omega = 7.29e-5                       # темп обертання Землі, рад/с
w = (0.0, 0.0, Omega)                 # ω = Ω·ẑ — вектор уздовж осі

for r in [(4.0, 3.0, 2.0), (4.0, 3.0, 9.0)]:      # та сама ρ, різна висота z
    a_cf = tuple(-c for c in cross(w, cross(w, r)))   # −ω×(ω×r) на одиницю маси
    rho  = math.hypot(r[0], r[1])                     # відстань до осі = √(x²+y²)
    coeff = tuple(round(c / Omega**2, 3) + 0.0 for c in a_cf)   # + 0.0: прибрати −0.0
    print(f"r={r} → a_вц = {coeff}·Ω²,  ρ={rho},  Ω²ρ={Omega**2*rho:.3e}")
