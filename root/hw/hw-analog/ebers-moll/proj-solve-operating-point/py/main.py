import math

# --- Параметри транзистора (Еберс — Молл у формі з I_S) ---
Vt   = 0.02585                 # тепловий потенціал, В (26 мВ при кімнатній)
I_S  = 1e-14                   # струм насичення транзистора, А
aF, aR = 0.99, 0.5             # коефіцієнти передавання (прямий / обернений)
I_ES, I_CS = I_S/aF, I_S/aR    # струми насичення переходів

# --- Схема ---
VBB, RB = 5.0, 220e3
VCC, RC = 5.0, 1.0e3

def device(vbe, vbc):
    """Струми виводів і провідності переходів у точці (vbe, vbc)."""
    IF = I_ES*(math.exp(vbe/Vt) - 1.0)     # прямий діод
    IR = I_CS*(math.exp(vbc/Vt) - 1.0)     # обернений діод
    Ic = aF*IF - IR
    Ib = (1 - aF)*IF + (1 - aR)*IR
    gF = (I_ES/Vt)*math.exp(vbe/Vt)        # dIF/dVbe
    gR = (I_CS/Vt)*math.exp(vbc/Vt)        # dIR/dVbc
    return Ic, Ib, gF, gR

def limit(vnew, vold, isat):
    """Обмеження стрибка напруги на переході — pnjlim із SPICE."""
    vcrit = Vt*math.log(Vt/(math.sqrt(2.0)*isat))
    if vnew > vcrit and abs(vnew - vold) > 2*Vt:
        if vold > 0:
            arg = 1.0 + (vnew - vold)/Vt
            return vold + Vt*math.log(arg) if arg > 0 else vcrit
        return Vt*math.log(vnew/Vt)
    return vnew

def solve(vb=0.0, vc=0.0, tol=1e-9, maxit=100):
    for k in range(maxit):
        vbe, vbc = vb, vb - vc
        Ic, Ib, gF, gR = device(vbe, vbc)

        # Нев'язки вузлових рівнянь (KCL)
        fB = (VBB - vb)/RB - Ib
        fC = (VCC - vc)/RC - Ic

        # Якобіан ∂(fB, fC)/∂(vb, vc)
        J11 = -1.0/RB - ((1 - aF)*gF + (1 - aR)*gR)
        J12 =  (1 - aR)*gR
        J21 = -aF*gF + gR
        J22 = -1.0/RC - gR

        # Розв'язок 2×2  J·Δ = −f  (правило Крамера)
        det = J11*J22 - J12*J21
        b1, b2 = -fB, -fC
        dvb = (J22*b1 - J12*b2)/det
        dvc = (J11*b2 - J21*b1)/det
        vb_new, vc_new = vb + dvb, vc + dvc

        # Обмежуємо стрибки напруг на ПЕРЕХОДАХ, тоді відновлюємо вузли
        vbe_l = limit(vb_new,          vbe, I_ES)
        vbc_l = limit(vb_new - vc_new, vbc, I_CS)
        vb_new, vc_new = vbe_l, vbe_l - vbc_l

        step = max(abs(vb_new - vb), abs(vc_new - vc))
        vb, vc = vb_new, vc_new
        if step < tol:
            return vb, vc, k + 1
    raise RuntimeError("не збіглося")

vb, vc, n = solve()
vbe, vbc = vb, vb - vc
Ic, Ib, gF, gR = device(vbe, vbc)
print(f"V_BE={vbe:.4f} В  V_CE={vc:.4f} В  "
      f"I_C={Ic*1e3:.4f} мА  I_B={Ib*1e6:.2f} мкА  "
      f"β={Ic/Ib:.1f}  за {n} ітерацій")
