#!/usr/bin/env python3
"""
torque_vectoring_controller.py
Контролер векторування крутного моменту для чотириколісної платформи.
Стабілізація курсової стійкості за рахунок диференціальної тяги коліс.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class VehicleParams:
    mass_kg: float = 1400.0       # Повна маса автомобіля (кг)
    track_width_m: float = 1.60   # Ширина колії коліс B (м)
    wheelbase_m: float = 2.65     # Колісна база L (м)
    wheel_radius_m: float = 0.32  # Радіус кочення колеса (м)
    understeer_grad: float = 0.002# Градієнт недостатньої повертальності K_us

class TorqueVectoringController:
    def __init__(self, p: VehicleParams):
        self.p = p
        self.kp_yaw = 2800.0  # Пропорційний коефіцієнт моменту (Н*м / (рад/с))

    def compute_yaw_control(
        self,
        velocity_ms: float,
        steer_angle_rad: float,
        current_yaw_rate: float,
        total_drive_torque_nm: float
    ) -> Tuple[float, List[float]]:
        """
        Розрахунок компенсувального моменту нишпорення Delta_Mz
        та розподіл тягових моментів на 4 колеса: [FL, FR, RL, RR].
        """
        # Бажана курсова швидкість за нейтральною моделлю велосипеда
        v = max(1.0, velocity_ms)
        yaw_rate_des = (v / (self.p.wheelbase_m + self.p.understeer_grad * (v ** 2))) * steer_angle_rad

        # Помилка за курсовою швидкістю
        yaw_err = yaw_rate_des - current_yaw_rate
        delta_mz = self.kp_yaw * yaw_err

        # Диференціальна тяга на осі: Delta_Fx = Delta_Mz / B
        delta_fx = delta_mz / self.p.track_width_m
        delta_torque_wheel = (delta_fx / 2.0) * self.p.wheel_radius_m

        base_t = total_drive_torque_nm / 4.0
        # Зовнішнє колесо додає тягу, внутрішнє зменшує
        t_fl = base_t - delta_torque_wheel
        t_fr = base_t + delta_torque_wheel
        t_rl = base_t - delta_torque_wheel
        t_rr = base_t + delta_torque_wheel

        return delta_mz, [round(t_fl, 1), round(t_fr, 1), round(t_rl, 1), round(t_rr, 1)]

def main():
    print("================================================================")
    print("КОНТРОЛЕР АКТИВНОГО ВЕКТОРУВАННЯ КРУТНОГО МОМЕНТУ (TORQUE VECTORING)")
    print("================================================================")
    ctrl = TorqueVectoringController(VehicleParams())

    # Вхід у лівий поворот на 72 км/год (20 м/с) із виникненням зносу передньої осі
    v = 20.0
    steer = math.radians(6.0)
    measured_yaw = 0.12  # робот повертає повільніше ніж задано кермом (підзнос)
    t_engine = 600.0

    delta_m, wheels = ctrl.compute_yaw_control(v, steer, measured_yaw, t_engine)

    print(f"Швидкість: 72 км/год, Кут керма: 6.0 град, Виміряна w_z: {measured_yaw} рад/с")
    print(f"Коригувальний повертальний момент Delta_Mz: {delta_m:.1f} Н*м")
    print(f"Розподіл крутного моменту по колесах [FL, FR, RL, RR]:")
    print(f"  Внутрішні колеса (L): {wheels[0]} Н*м (розвантаження тяги)")
    print(f"  Зовнішні колеса  (R): {wheels[1]} Н*м (додаткова штовхаюча тяга)")
    print("================================================================")

if __name__ == "__main__":
    main()
