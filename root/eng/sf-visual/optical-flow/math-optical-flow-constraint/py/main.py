import math

# LK по вікну (2*R+1)×(2*R+1) навколо (x,y). tau — поріг на менше власне число.
# prev, curr — 8-бітні яскравості рядками по W пікселів (плоскі списки/масиви).
# Повертає (u, v, ok); ok=False → точка ненадійна.
def lk_flow(prev, curr, W, x, y, R, tau):
    # елементи структурного тензора AᵀA і правого вектора Aᵀb
    Axx = Axy = Ayy = 0.0   # Σ Iₓ², Σ IₓIᵧ, Σ Iᵧ²
    bx = by = 0.0           # Σ IₓIₜ, Σ IᵧIₜ

    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            px, py = x + dx, y + dy
            # просторовий градієнт — центральні різниці по поточному кадру
            Ix = 0.5 * (curr[py*W + px+1] - curr[py*W + px-1])
            Iy = 0.5 * (curr[(py+1)*W + px] - curr[(py-1)*W + px])
            # часова похідна — різниця між кадрами в тій самій точці
            It = curr[py*W + px] - prev[py*W + px]

            Axx += Ix*Ix;   Axy += Ix*Iy;   Ayy += Iy*Iy
            bx  += Ix*It;   by  += Iy*It

    # надійність: визначник і слід тензора → менше власне число λ₂
    det   = Axx*Ayy - Axy*Axy
    trace = Axx + Ayy
    # λ₂ = (trace − √(trace² − 4·det)) / 2  — менший з двох власних чисел
    disc  = max(0.0, trace*trace - 4.0*det)
    lambda_min = 0.5 * (trace - math.sqrt(disc))
    if lambda_min < tau or det < 1e-6:
        return (0.0, 0.0, False)   # майже вироджена → відкинути

    # розв'язок 2×2:  AᵀA · w = −Aᵀb  →  w = −(AᵀA)⁻¹ · Aᵀb
    u = -( Ayy*bx - Axy*by) / det
    v = -(-Axy*bx + Axx*by) / det
    return (u, v, True)
