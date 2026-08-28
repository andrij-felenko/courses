import numpy as np


class Cap:
    """Реальний конденсатор: ємність C, паразитна індуктивність монтажу ESL,
    опір втрат ESR. n однакових штук у паралель."""
    def __init__(self, C, esr, esl, n=1):
        self.C, self.esr, self.esl, self.n = C, esr, esl, n

    def admittance(self, w):                      # w — масив колових частот
        z = self.esr + 1j * w * self.esl + 1.0 / (1j * w * self.C)
        return self.n / z                         # n у паралель → провідність ×n


class VRM:
    """Стабілізатор як R + jωL: нижче смуги петлі керування тримає шину малим
    опором, вище — здається просто індуктивністю виходу."""
    def __init__(self, esr, esl):
        self.esr, self.esl = esr, esl

    def admittance(self, w):
        return 1.0 / (self.esr + 1j * w * self.esl)


def pdn_impedance(freqs, vrm, caps):
    """|Z(f)| паралельного поєднання VRM і всіх конденсаторів — на всій сітці."""
    w = 2 * np.pi * freqs
    Y = vrm.admittance(w)
    for c in caps:
        Y += c.admittance(w)                      # провідності просто додаються
    return 1.0 / Y                                # комплексний Z, поелементно


def analyse(name, vrm, caps, z_target, f_lo=1e3, f_hi=50e6, n=4000):
    f = np.logspace(np.log10(f_lo), np.log10(f_hi), n)   # логарифмічна сітка
    Z = np.abs(pdn_impedance(f, vrm, caps))
    i = int(np.argmax(Z))                         # найгірша точка всієї смуги
    ok = Z[i] <= z_target
    ntot = sum(c.n for c in caps)
    print(f"[{name}]  {ntot} конденсаторів,  ціль Z_ціль = {z_target*1e3:.0f} мОм")
    print(f"    найгірше   |Z|max = {Z[i]*1e3:6.1f} мОм @ {f[i]/1e6:5.2f} МГц"
          f"   ({Z[i]/z_target:.1f}× цілі)  ->  {'PASS' if ok else 'FAIL'}")
    # піки антирезонансу — локальні максимуми кривої, що вилізли над стелю
    for k in range(1, n - 1):
        if Z[k] > Z[k-1] and Z[k] > Z[k+1] and Z[k] > z_target:
            print(f"    антирезонанс {Z[k]*1e3:6.1f} мОм @ {f[k]/1e6:5.2f} МГц"
                  f"  (протикає ціль)")
    print()
    return ok


if __name__ == "__main__":
    vrm = VRM(esr=2e-3, esl=6.4e-9)
    Z_CIL = 10e-3                                  # стеля: 1.0 В ±5% при кидку 5 А

    # наївна мережа: один об'ємний плюс банка дрібної кераміки
    naive = [Cap(100e-6, 5e-3,  3.5e-9),          # 1× 100 мкФ (об'ємний)
             Cap(100e-9, 40e-3, 2.0e-9, n=10)]    # 10× 100 нФ (кераміка)

    # виправлена: сходинки між номіналами замість прірви
    fixed = [Cap(100e-6, 5e-3,  2.8e-9, n=2),     # 2× 100 мкФ
             Cap(10e-6,  3e-3,  1.6e-9, n=6),     # 6× 10 мкФ  — місток
             Cap(1e-6,   8e-3,  1.4e-9, n=12),    # 12× 1 мкФ  — місток
             Cap(100e-9, 40e-3, 1.3e-9, n=24)]    # 24× 100 нФ

    analyse("наївна",     vrm, naive, Z_CIL)
    analyse("виправлена", vrm, fixed, Z_CIL)
