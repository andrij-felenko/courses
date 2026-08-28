import math
from dataclasses import dataclass
from typing import List, Tuple

R_GAS = 8.314462618  # Універсальна газова стала, Дж/(моль·К)

@dataclass
class StatePoint:
    name: str
    pressure_pa: float
    volume_m3: float
    temp_k: float

@dataclass
class CarnotResults:
    points: List[StatePoint]
    q_h_j: float
    q_c_j: float
    work_j: float
    efficiency: float
    cop_ref: float
    cop_heat: float

def simulate_carnot_cycle(
    n_moles: float,
    t_h: float,
    t_c: float,
    p1_pa: float,
    v1_m3: float,
    r_v: float,
    gamma: float = 1.4
) -> CarnotResults:
    """Обчислює чотири стани та енергетичні параметри циклу Карно."""
    if t_c <= 0 or t_h <= 0:
        raise ValueError("Температури повинні бути строго додатними в Кельвінах")
    if t_c >= t_h:
        raise ValueError("Температура холодильника T_C мусить бути меншою за T_H")
    if r_v <= 1.0:
        raise ValueError("Ступінь розширення r_v мусить бути більшим за 1.0")

    # Точка 1
    p1, v1 = p1_pa, v1_m3
    
    # Точка 2: ізотермічне розширення при T_H
    v2 = v1 * r_v
    p2 = p1 / r_v
    
    # Точка 3: адіабатичне розширення до T_C
    vol_ratio_adiabat = (t_h / t_c) ** (1.0 / (gamma - 1.0))
    v3 = v2 * vol_ratio_adiabat
    p3 = (n_moles * R_GAS * t_c) / v3
    
    # Точка 4: ізотермічне стискання при T_C
    v4 = v1 * vol_ratio_adiabat
    p4 = (n_moles * R_GAS * t_c) / v4

    points = [
        StatePoint("1 (Початок розширення)", p1, v1, t_h),
        StatePoint("2 (Кінець ізотерми T_H)", p2, v2, t_h),
        StatePoint("3 (Кінець адіабати)", p3, v3, t_c),
        StatePoint("4 (Кінець ізотерми T_C)", p4, v4, t_c),
    ]

    # Енергетичні величини
    q_h = n_moles * R_GAS * t_h * math.log(r_v)
    q_c = n_moles * R_GAS * t_c * math.log(r_v)
    work = q_h - q_c
    
    efficiency = 1.0 - (t_c / t_h)
    cop_ref = t_c / (t_h - t_c)
    cop_heat = t_h / (t_h - t_c)

    return CarnotResults(points, q_h, q_c, work, efficiency, cop_ref, cop_heat)

if __name__ == "__main__":
    # Приклад: 1 моль гелію (одноатомний газ, gamma = 1.667)
    res = simulate_carnot_cycle(
        n_moles=1.0,
        t_h=600.0,
        t_c=300.0,
        p1_pa=1e6,      # 10 бар
        v1_m3=0.0025,   # 2.5 літра
        r_v=2.0,        # розширення удвічі
        gamma=1.667
    )

    print("=== ТОЧКИ СТАНУ ЦИКЛУ КАРНО ===")
    for pt in res.points:
        print(f"Стан {pt.name}: P = {pt.pressure_pa/1e5:.3f} бар, V = {pt.volume_m3*1000:.3f} л, T = {pt.temp_k:.1f} K")

    print("\n=== ЕНЕРГЕТИЧНИЙ БАЛАНС ===")
    print(f"Підведена теплота Q_H : {res.q_h_j:.2f} Дж")
    print(f"Скинута теплота Q_C   : {res.q_c_j:.2f} Дж")
    print(f"Корисна робота W      : {res.work_j:.2f} Дж")
    print(f"Термічний ККД η       : {res.efficiency * 100:.2f}%")
    print(f"COP холодильника      : {res.cop_ref:.2f}")
    print(f"COP теплового насоса  : {res.cop_heat:.2f}")
