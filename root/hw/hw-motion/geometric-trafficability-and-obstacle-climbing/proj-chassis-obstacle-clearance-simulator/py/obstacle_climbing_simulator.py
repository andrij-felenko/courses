#!/usr/bin/env python3
"""
obstacle_climbing_simulator.py
Симулятор геометричної прохідності колісного шасі: розрахунок критичних
кутів звисів, рампи та граничної висоти подолання вертикальних уступів.
"""

import math
import sys
from dataclasses import dataclass
from typing import Tuple

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

@dataclass
class ChassisParams:
    wheelbase_m: float = 0.65            # Колісна база L_base (м)
    wheel_radius_m: float = 0.125        # Радіус колеса R (м)
    ground_clearance_m: float = 0.090    # Дорожній просвіт h (м)
    front_overhang_m: float = 0.080      # Передній звис a_front (м)
    rear_overhang_m: float = 0.090       # Задній звис a_rear (м)
    friction_mu: float = 0.85            # Коефіцієнт зчеплення колеса з уступом
    total_mass_kg: float = 24.0          # Повна маса платформи (кг)

class ObstacleClimbingSimulator:
    def __init__(self, p: ChassisParams):
        self.p = p

    def geometric_angles(self):
        """Розрахунок ключових кутів прохідності."""
        approach_rad = math.atan2(self.p.ground_clearance_m, self.p.front_overhang_m)
        departure_rad = math.atan2(self.p.ground_clearance_m, self.p.rear_overhang_m)
        ramp_rad = 2.0 * math.atan2(2.0 * self.p.ground_clearance_m, self.p.wheelbase_m)
        return math.degrees(approach_rad), math.degrees(departure_rad), math.degrees(ramp_rad)

    def calculate_climbing_limit(self, step_height_m: float) -> Tuple[bool, float]:
        """
        Аналіз можливості заїзду на уступ висотою step_height_m.
        Повертає (чи можливий заїзд, необхідний момент на колесі Н*м).
        """
        r = self.p.wheel_radius_m
        if step_height_m >= r * 0.95:
            return False, float('inf')

        theta = math.acos(max(-1.0, min(1.0, 1.0 - step_height_m / r)))
        g = 9.81
        fn_per_front_wheel = (self.p.total_mass_kg * g * 0.5) / 2.0

        sin_t = math.sin(theta)
        cos_t = math.cos(theta)
        mu = self.p.friction_mu

        denom = cos_t + mu * sin_t
        if denom <= 0.01:
            return False, float('inf')

        f_drive_req = (fn_per_front_wheel * sin_t) / denom
        if f_drive_req > mu * fn_per_front_wheel * 1.5:
            return False, f_drive_req * r

        t_motor_req = f_drive_req * r
        return True, t_motor_req

def main():
    print('================================================================')
    print('ОЦІНКА ГЕОМЕТРИЧНОЇ ПРОХІДНОСТІ ТА ПОДОЛАННЯ УСТУПІВ ШАСІ')
    print('================================================================')
    sim = ObstacleClimbingSimulator(ChassisParams())
    appr, dep, ramp = sim.geometric_angles()

    print(f"Кут в'їзду (передній звис): {appr:.1f} град.")
    print(f"Кут з'їзду  (задній звис):  {dep:.1f} град.")
    print(f"Поздовжній кут рампи:       {ramp:.1f} град.")
    print('----------------------------------------------------------------')
    for h_cm in [4.0, 7.0, 9.0, 11.0]:
        h_m = h_cm / 100.0
        ok, t_req = sim.calculate_climbing_limit(h_m)
        status = 'УСПІШНИЙ ЗАЇЗД' if ok else 'НЕ ПРОХОДИТЬ (БУКСУВАННЯ / ВИСЕННЯ)'
        print(f'Уступ h = {h_cm:4.1f} см ({h_m/sim.p.wheel_radius_m*100:2.0f}% радіуса): {status:35s} | Т_необхідний = {t_req:.2f} Н*м')
    print('================================================================')

if __name__ == '__main__':
    main()
