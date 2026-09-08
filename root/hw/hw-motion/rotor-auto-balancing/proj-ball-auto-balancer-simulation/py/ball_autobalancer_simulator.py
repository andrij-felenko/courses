#!/usr/bin/env python3
"""
ball_autobalancer_simulator.py
Чисельне моделювання кулькового автобалансира надкритичного ротора:
проходження резонансу та компенсація дисбалансу кульками в протифазі.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class BalancerParams:
    rotor_mass_kg: float = 4.5           # Маса ротора (кг)
    unbalance_mass_kg: float = 0.08      # Маса дисбалансу (кг)
    eccentricity_m: float = 0.035        # Ексцентриситет дисбалансу e (м)
    ball_mass_kg: float = 0.05           # Маса однієї кульки (кг, всього 2 шт)
    race_radius_m: float = 0.060         # Радіус бігової доріжки R_b (м)
    critical_speed_rad_s: float = 60.0   # Резонансна критична частота omega_cr
    damping_ratio: float = 0.08          # Коефіцієнт демпфування опори

class BallAutoBalancerSimulator:
    def __init__(self, p: BalancerParams):
        self.p = p

    def evaluate_steady_state(self, speed_rad_s: float) -> Tuple[float, float, float]:
        """
        Розрахунок амплітуди вібрацій ротора без балансира та з балансиром.
        Повертає (амплітуда без балансира мкм, амплітуда з балансиром мкм, кут розходження кульок град).
        """
        eta = speed_rad_s / self.p.critical_speed_rad_s
        denom = math.sqrt((1.0 - eta**2)**2 + (2.0 * self.p.damping_ratio * eta)**2)

        # Амплітуда вібрацій без балансира
        x_unbalanced_m = (self.p.unbalance_mass_kg * self.p.eccentricity_m / self.p.rotor_mass_kg) * (eta**2 / denom)

        # У надкритичній зоні (eta > sqrt(2)) автобалансир стабільний
        if eta > 1.414:
            # Необхідний протифазний момент 2 * m_b * R_b * cos(psi/2) = m_u * e
            val = (self.p.unbalance_mass_kg * self.p.eccentricity_m) / (2.0 * self.p.ball_mass_kg * self.p.race_radius_m)
            val = min(0.999, max(-0.999, val))
            half_angle = math.acos(val)
            ball_angle_deg = math.degrees(2.0 * half_angle)
            # Залишкова вібрація за рахунок недосконалості доріжки (до 5% від початкової)
            x_balanced_m = x_unbalanced_m * 0.04
        else:
            ball_angle_deg = 0.0
            x_balanced_m = x_unbalanced_m * 1.3  # у підкритиці кульки дещо підсилюють вібрацію

        return x_unbalanced_m * 1e6, x_balanced_m * 1e6, ball_angle_deg

def main():
    print("================================================================")
    print("МОДЕЛЮВАННЯ КУЛЬКОВОГО АВТОБАЛАНСИРА НАДКРИТИЧНОГО РОТОРА")
    print("================================================================")
    sim = BallAutoBalancerSimulator(BalancerParams())

    print("Швидкість обертання | Без балансира | З автобалансиром | Ефективність")
    print("----------------------------------------------------------------")
    for omega_ratio in [0.5, 1.0, 1.5, 2.5]:
        omega = omega_ratio * sim.p.critical_speed_rad_s
        x_no, x_yes, angle = sim.evaluate_steady_state(omega)
        eff = max(0.0, (x_no - x_yes) / x_no * 100.0) if x_no > 0 else 0
        state = "РЕЗОНАНС" if omega_ratio == 1.0 else ("НАДКРИТИКА" if omega_ratio > 1.4 else "ПІДКРИТИКА")
        print(f"eta = {omega_ratio:4.1f} ({state:10s}) | {x_no:8.1f} мкм | {x_yes:8.1f} мкм    | {eff:5.1f}%")
    print("================================================================")

if __name__ == "__main__":
    main()
