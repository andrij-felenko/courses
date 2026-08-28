import numpy as np
import matplotlib.pyplot as plt

Vt = 0.025852                       # kT/q при 300 K, В

# --- числа просто з рядка .model 2N3904 (Fairchild) ---
p = dict(IS=6.734e-15, BF=416.4, NF=1.0,
         IKF=66.78e-3, ISE=6.734e-15, NE=1.259, VAF=74.03)

def gummel_poon(vbe, vbc=0.0, p=p, Vt=Vt):
    """I_К, I_Б, β у прямому активному режимі; vbe — число або масив."""
    ef = np.exp(vbe / (p['NF'] * Vt))
    er = np.exp(vbc / Vt)
    q1 = 1.0 / (1.0 - vbc / p['VAF'])                  # звуження бази (Ерлі)
    q2 = (p['IS'] / p['IKF']) * (ef - 1.0)             # високий рівень інжекції
    qb = 0.5 * q1 * (1.0 + np.sqrt(1.0 + 4.0 * q2))    # нормований заряд бази
    ic = p['IS'] / qb * (ef - er)
    ib = p['IS'] / p['BF'] * (ef - 1.0) + p['ISE'] * (np.exp(vbe / (p['NE'] * Vt)) - 1.0)
    return ic, ib, ic / ib

vbe = np.linspace(0.30, 0.85, 400)
ic, ib, beta = gummel_poon(vbe)          # V_BC = 0 — це і є графік Ґуммеля

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.semilogy(vbe, ic, label='I_К'); ax1.semilogy(vbe, ib, label='I_Б')
ax1.set_xlabel('V_BE, В'); ax1.set_ylabel('струм, А'); ax1.legend(); ax1.grid(True, which='both')
ax2.semilogx(ic, beta); ax2.set_xlabel('I_К, А'); ax2.set_ylabel('β'); ax2.grid(True)
plt.tight_layout(); plt.show()

i = beta.argmax()
print(f"β_макс = {beta[i]:.0f} при I_К = {ic[i]*1e3:.1f} мА;  BF = {p['BF']}")
