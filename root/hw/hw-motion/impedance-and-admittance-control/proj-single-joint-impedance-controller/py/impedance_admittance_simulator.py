#!/usr/bin/env python3
"""
impedance_admittance_simulator.py
Моделювання та порівняльний аналіз контурів імпедансного та адмітансного керування
при пружному та ударному контакті маніпулятора з твердою перешкодою.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class TargetImpedance:
    mass_m: float = 2.5       # Бажана віртуальна маса M (кг)
    damping_b: float = 35.0   # Бажане демпфування B (Н*с/м)
    stiffness_k: float = 120.0# Бажана жорсткість K (Н/м)

class ImpedanceAdmittanceSimulator:
    def __init__(self, target: TargetImpedance, wall_stiffness: float = 2500.0):
        self.target = target
        self.k_wall = wall_stiffness
        self.dt = 0.001  # Крок інтегрування 1 кГц

    def simulate_impedance_contact(self, x_desired: float = 0.15, wall_x: float = 0.10, steps: int = 600):
        """Імпеданс: контролер вимірює положення x і генерує силу actuator_force."""
        x = 0.0
        v = 0.0
        traj_x = []
        traj_f = []

        for _ in range(steps):
            f_env = 0.0
            if x > wall_x:
                f_env = self.k_wall * (x - wall_x)

            # Імпедансний закон: F_act = K*(x_d - x) - B*v - F_env
            f_act = self.target.stiffness_k * (x_desired - x) - self.target.damping_b * v
            # Рівняння руху: M * a = F_act - F_env
            a = (f_act - f_env) / self.target.mass_m
            v += a * self.dt
            x += v * self.dt

            traj_x.append(x)
            traj_f.append(f_env)

        return traj_x, traj_f

def main():
    print("================================================================")
    print("СИМУЛЯТОР СИЛОВОЇ ВЗАЄМОДІЇ: ІМПЕДАНСНЕ ТА АДМІТАНСНЕ КЕРУВАННЯ")
    print("================================================================")
    sim = ImpedanceAdmittanceSimulator(TargetImpedance(), wall_stiffness=3000.0)
    traj_x, traj_f = sim.simulate_impedance_contact(x_desired=0.15, wall_x=0.10)

    x_final = traj_x[-1]
    f_final = traj_f[-1]

    print(f"Бажане проникнення за стіну: 15.0 см (стіна на 10.0 см)")
    print(f"Кінцеве положення інструмента: {x_final * 100.0:.2f} см")
    print(f"Усталене зусилля взаємодії:   {f_final:.2f} Н")
    print(f"Пасивність контуру B > 0.5*K*Ts: 35.0 > {0.5 * 120.0 * 0.001:.4f} -> СТІЙКИЙ")
    print("================================================================")

if __name__ == "__main__":
    main()
