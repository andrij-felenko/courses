import math
from typing import Dict, Union, Tuple

def calc_4probe_sheet_resistance(
    voltage_v: float,
    current_a: float,
    probe_spacing_m: float,
    thickness_m: float = 0.0,
    edge_distance_m: float = float('inf')
) -> Dict[str, float]:
    """
    Обчислює поверхневий та питомий опір за даними колонеарного 4-зондового вимірювання.
    """
    if current_a <= 0 or voltage_v <= 0 or probe_spacing_m <= 0:
        raise ValueError("Струм, напруга та крок між зондами повинні бути додатними.")

    r_raw = voltage_v / current_a
    c_base = math.pi / math.log(2.0)  # ≈ 4.53236014

    # Поправка на товщину плівки (d / s)
    c_thick = 1.0
    if thickness_m > 0 and thickness_m / probe_spacing_m > 0.05:
        d_s = thickness_m / probe_spacing_m
        c_thick = (math.pi * d_s) / math.log(math.sinh(d_s) / math.sinh(d_s / 2.0))
        c_thick = c_thick / c_base  # нормування відносно межі тонкої плівки

    # Поправка на край зразка (x / s)
    c_edge = 1.0
    if not math.isinf(edge_distance_m) and edge_distance_m > 0:
        x_s = edge_distance_m / probe_spacing_m
        term = ((2.0 * x_s) ** 2 + 1.0) / ((2.0 * x_s) ** 2 + 4.0)
        c_edge = 1.0 / (1.0 + (1.0 / math.log(2.0)) * math.log(term))

    r_sheet = r_raw * c_base * c_thick * c_edge
    resistivity = r_sheet * thickness_m if thickness_m > 0 else 0.0

    return {
        "r_raw_ohm": r_raw,
        "r_sheet_ohm_sq": r_sheet,
        "resistivity_ohm_m": resistivity,
        "c_total_factor": c_base * c_thick * c_edge
    }


def solve_van_der_pauw(r_a: float, r_b: float, tol: float = 1e-7, max_iter: int = 100) -> float:
    """
    Чисельно розв'язує рівняння Ван дер Пау методом Ньютона — Рафсона.
    exp(-π R_A / R_s) + exp(-π R_B / R_s) = 1
    """
    if r_a <= 0 or r_b <= 0:
        raise ValueError("Опори R_A та R_B повинні бути додатними.")

    # Початкове наближення
    r_s = (math.pi / math.log(2.0)) * ((r_a + r_b) / 2.0)

    for _ in range(max_iter):
        f_val = math.exp(-math.pi * r_a / r_s) + math.exp(-math.pi * r_b / r_s) - 1.0
        # Похідна df/dR_s
        df_drs = (math.pi * r_a / (r_s ** 2)) * math.exp(-math.pi * r_a / r_s) + \
                 (math.pi * r_b / (r_s ** 2)) * math.exp(-math.pi * r_b / r_s)

        dr_s = f_val / df_drs
        r_s -= dr_s

        if abs(dr_s) < tol:
            return r_s

    raise RuntimeError("Не вдалося досягти збіжності за max_iter ітерацій.")


if __name__ == "__main__":
    res = calc_4probe_sheet_resistance(
        voltage_v=0.04532, current_a=0.001, probe_spacing_m=0.001, thickness_m=1e-7
    )
    print(f"Поверхневий опір: {res['r_sheet_ohm_sq']:.4f} Ом/□")
    print(f"Питомий опір: {res['resistivity_ohm_m']:.6e} Ом·м")

    vdp_rs = solve_van_der_pauw(r_a=10.2, r_b=11.5)
    print(f"Ван дер Пау R_s: {vdp_rs:.4f} Ом/□")
