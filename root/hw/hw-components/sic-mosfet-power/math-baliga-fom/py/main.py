EPS0 = 8.854e-14        # Ф/см — проникність вакууму

# (відносна проникність, рухливість см²/(В·с), критичне поле В/см)
MAT = {
    "Si":     (11.7, 1350, 0.30e6),
    "4H-SiC": ( 9.7,  950, 2.80e6),
    "GaN":    ( 9.0, 1250, 3.30e6),
}

def bfom(er, mu, ec):
    return er * EPS0 * mu * ec ** 3        # Вт/см²

base = bfom(*MAT["Si"])
print(f"BFOM(Si) = {base:.3g} Вт/см²  — точка відліку\n")

for name, (er, mu, ec) in MAT.items():
    er_si, mu_si, ec_si = MAT["Si"]
    k_eps = er / er_si                     # внесок проникності
    k_mu  = mu / mu_si                     # внесок рухливості
    k_ec  = (ec / ec_si) ** 3              # внесок куба поля
    print(f"{name:7s}  ε×{k_eps:.2f}  μ×{k_mu:.2f}  поле³×{k_ec:7.1f}"
          f"  →  разом ×{bfom(er, mu, ec) / base:.0f}")
