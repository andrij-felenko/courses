#!/usr/bin/env python3
"""
proprioceptive_force_estimator.py
Оцінювач зовнішнього контактного зусилля квазіпрямого привода (QDD)
на основі квадратурного струму мотора Iq без використання зовнішніх датчиків сили.
"""

import math
from dataclasses import dataclass

@dataclass
class ActuatorSpecs:
    torque_constant_kt: float = 0.095    # Коефіцієнт мотора Kt (Н*м / А)
    gear_ratio_n: float = 6.0            # Передавальне число планетарки N
    rotor_inertia_kgm2: float = 0.00012  # Інерція ротора (кг*м^2)
    coulomb_friction_nm: float = 0.18    # Тертя Кулона в редукторі (Н*м)
    viscous_damping_nms: float = 0.012   # В'язке демпфування (Н*м*с/рад)
    efficiency: float = 0.92             # ККД прямого/зворотного ходу

class ProprioceptiveForceEstimator:
    def __init__(self, specs: ActuatorSpecs):
        self.specs = specs

    def estimate_external_torque(
        self,
        current_iq_amps: float,
        joint_velocity_rad_s: float,
        joint_accel_rad_s2: float
    ) -> float:
        """
        Оцінка зовнішнього моменту на вихідному валу:
        tau_ext = tau_em - tau_inertia - tau_friction
        """
        # 1. Електромагнітний момент
        tau_em = self.specs.torque_constant_kt * current_iq_amps * self.specs.gear_ratio_n * self.specs.efficiency

        # 2. Інерційний опір розгону ротора
        reflected_inertia = self.specs.rotor_inertia_kgm2 * (self.specs.gear_ratio_n ** 2)
        tau_inertial = reflected_inertia * joint_accel_rad_s2

        # 3. Власні втрати на тертя в редукторі
        sign = 1.0 if joint_velocity_rad_s > 0 else (-1.0 if joint_velocity_rad_s < 0 else 0.0)
        tau_fric = sign * self.specs.coulomb_friction_nm + self.specs.viscous_damping_nms * joint_velocity_rad_s

        # 4. Зовнішній реактивний момент від середовища
        tau_ext = tau_em - tau_inertial - tau_fric
        return round(tau_ext, 3)

def main():
    print("================================================================")
    print("ПРОПРІОЦЕПТИВНИЙ ОЦІНЮВАЧ ЗУСИЛЛЯ QDD-ПРИВОДА (БЕЗ ДАТЧИКА СИЛИ)")
    print("================================================================")
    estimator = ProprioceptiveForceEstimator(ActuatorSpecs())

    # Тест 1: вільний рух без контакту
    t_free = estimator.estimate_external_torque(current_iq_amps=0.45, joint_velocity_rad_s=5.0, joint_accel_rad_s2=0.0)
    # Тест 2: упор у перешкоду (високий струм при нульовій швидкості)
    t_contact = estimator.estimate_external_torque(current_iq_amps=8.2, joint_velocity_rad_s=0.0, joint_accel_rad_s2=0.0)

    print(f"Тест 1 (вільний рух при 5 рад/с, Iq = 0.45 А): tau_ext = {t_free} Н*м (~0 Н*м, шум)")
    print(f"Тест 2 (контакт з об'єктом, Iq = 8.2 А):       tau_ext = {t_contact} Н*м (ЗАСІЧЕНО КОНТАКТ)")
    print(f"Точність оцінки сили при плечі важеля 0.25 м: F_ext = {t_contact / 0.25:.1f} Н")
    print("================================================================")

if __name__ == "__main__":
    main()
