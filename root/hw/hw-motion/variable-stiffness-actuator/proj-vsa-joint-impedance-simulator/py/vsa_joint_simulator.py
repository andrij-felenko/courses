#!/usr/bin/env python3
"""
vsa_joint_simulator.py
Динамічне моделювання шарніра з регульованою жорсткістю (Variable Stiffness Actuator).
Демонстрація м'якого режиму (безпечна взаємодія) та жорсткого режиму (прецизійність).
"""

import math
from dataclasses import dataclass

@dataclass
class VSAParams:
    link_inertia: float = 0.08      # Момент інерції вихідної ланки (кг*м^2)
    link_damping: float = 0.45      # Коефіцієнт демпфування (Н*м*с/рад)
    k_base: float = 15.0            # Базова лінійна жорсткість (Н*м/рад)
    k_nonlinear: float = 450.0      # Нелінійний коефіцієнт кулачка/пружини

class VSAJointSimulator:
    def __init__(self, p: VSAParams):
        self.p = p

    def joint_stiffness(self, deflection_rad: float, tension_sigma: float) -> float:
        """Фізична миттєва жорсткість шарніра K = d(tau)/d(theta) [Н*м/рад]."""
        return self.p.k_base + 3.0 * self.p.k_nonlinear * (deflection_rad ** 2) * (1.0 + 4.0 * tension_sigma)

    def spring_torque(self, deflection_rad: float, tension_sigma: float) -> float:
        """Пружний відновлювальний момент нелінійної пружини [Н*м]."""
        return self.p.k_base * deflection_rad + self.p.k_nonlinear * (deflection_rad ** 3) * (1.0 + 4.0 * tension_sigma)

def main():
    print("================================================================")
    print("СИМУЛЯТОР АКТУАТОРА ЗІ ЗМІННОЮ МЕХАНІЧНОЮ ЖОРСТКІСТЮ (VSA)")
    print("================================================================")
    vsa = VSAJointSimulator(VSAParams())

    deflection = math.radians(8.0)  # відхилення ланки 8 градусів під навантаженням

    # М'який режим: натяг sigma = 0.0 (кобот / взаємодія з людиною)
    k_soft = vsa.joint_stiffness(deflection, tension_sigma=0.0)
    t_soft = vsa.spring_torque(deflection, tension_sigma=0.0)

    # Жорсткий режим: натяг sigma = 1.0 (високоточне позиціювання)
    k_hard = vsa.joint_stiffness(deflection, tension_sigma=1.0)
    t_hard = vsa.spring_torque(deflection, tension_sigma=1.0)

    print(f"Кут пружного відхилення ланки: 8.0 градусів ({deflection:.3f} рад)")
    print(f"М'який режим   (sigma = 0.0): K = {k_soft:6.1f} Н*м/рад | Момент = {t_soft:5.2f} Н*м (БЕЗПЕКА HRI)")
    print(f"Жорсткий режим (sigma = 1.0): K = {k_hard:6.1f} Н*м/рад | Момент = {t_hard:5.2f} Н*м (ШВИДКІСТЬ/ТОЧНІСТЬ)")
    print(f"Діапазон адаптації жорсткості: 1 : {k_hard / k_soft:.1f} без заміни пружин!")
    print("================================================================")

if __name__ == "__main__":
    main()
