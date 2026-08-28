# vdp_solver.py — Професійний модуль обробки вимірювань Ван дер Пау на Python 3
import math
from typing import NamedTuple, Optional, Tuple

PI = math.pi
LN2 = math.log(2.0)

class VdpResult(NamedTuple):
    sheet_resistance: float  # Поверхневий опір R_s в Ом/квадрат
    resistivity: float       # Об'ємний питомий опір ρ в Ом·см
    asymmetry_ratio: float   # Коефіцієнт асиметрії R_A / R_B
    iterations: int          # Кількість ітерацій Ньютона
    converged: bool          # Прапорець успішної збіжності

def solve_vdp_sheet_resistance(r_a: float, r_b: float, tol: float = 1e-9, max_iter: int = 50) -> Tuple[float, int, bool]:
    """
    Чисельне розв'язання рівняння exp(-pi*R_A/R_s) + exp(-pi*R_B/R_s) = 1
    методом Ньютона-Рафсона.
    """
    if r_a <= 0.0 or r_b <= 0.0:
        raise ValueError("Опори R_A та R_B повинні бути строго додатними числами")

    # Початкове наближення за аналітичною формулою симетричного зразка
    r_s = (PI / (2.0 * LN2)) * (r_a + r_b)

    for i in range(1, max_iter + 1):
        e_a = math.exp(-PI * r_a / r_s)
        e_b = math.exp(-PI * r_b / r_s)

        f_val = e_a + e_b - 1.0
        f_der = (PI * r_a / (r_s * r_s)) * e_a + (PI * r_b / (r_s * r_s)) * e_b

        if abs(f_der) < 1e-15:
            break

        delta = f_val / f_der
        r_s -= delta

        if abs(delta / r_s) < tol:
            return r_s, i, True

    return r_s, max_iter, False

def process_vdp_measurements(
    voltages_a: Tuple[float, float, float, float],
    voltages_b: Tuple[float, float, float, float],
    current: float,
    thickness_cm: float,
    temp_c: float = 20.0,
    tcr: float = 0.0
) -> Optional[VdpResult]:
    """
    Обробка 8 вимірювань напруги із 2 полярностями струму.
    voltages_a: (V_DC+, V_DC-, V_CD+, V_CD-)
    voltages_b: (V_AD+, V_AD-, V_DA+, V_DA-)
    current: вимірювальний струм в Амперах
    thickness_cm: товщина зразка в см
    """
    if current <= 0.0 or thickness_cm <= 0.0:
        return None

    # Реверсивне 8-точкове усереднення для компенсації термо-ЕРС
    v_a1 = (voltages_a[0] - voltages_a[1]) / (2.0 * current)
    v_a2 = (voltages_a[2] - voltages_a[3]) / (2.0 * current)
    r_a = (v_a1 + v_a2) / 2.0

    v_b1 = (voltages_b[0] - voltages_b[1]) / (2.0 * current)
    v_b2 = (voltages_b[2] - voltages_b[3]) / (2.0 * current)
    r_b = (v_b1 + v_b2) / 2.0

    r_s_raw, iters, ok = solve_vdp_sheet_resistance(r_a, r_b)
    if not ok:
        return None

    # Температурна корекція до 20 °C
    r_s = r_s_raw / (1.0 + tcr * (temp_c - 20.0))
    rho = r_s * thickness_cm
    ratio = max(r_a, r_b) / min(r_a, r_b)

    return VdpResult(
        sheet_resistance=r_s,
        resistivity=rho,
        asymmetry_ratio=ratio,
        iterations=iters,
        converged=ok
    )

if __name__ == "__main__":
    res = process_vdp_measurements(
        voltages_a=(0.0123, -0.0121, 0.0124, -0.0122),
        voltages_b=(0.0185, -0.0183, 0.0186, -0.0184),
        current=0.010,       # 10 мА
        thickness_cm=0.05,   # 500 мкм
        temp_c=25.0,
        tcr=0.00393
    )
    if res:
        print(f"Поверхневий опір R_s: {res.sheet_resistance:.4f} Ом/кв")
        print(f"Питомий опір rho:     {res.resistivity * 1e3:.4f} мОм·см")
        print(f"Асиметрія R_A/R_B:     {res.asymmetry_ratio:.3f}")
        print(f"Збіжність за {res.iterations} ітерацій")
