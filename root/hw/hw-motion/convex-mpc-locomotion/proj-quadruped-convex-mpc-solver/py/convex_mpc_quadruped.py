#!/usr/bin/env python3
"""
convex_mpc_quadruped.py
Спрощений опуклий MPC-контролер для стабілізації ходьби чотириногого робота (quadruped).
Розрахунок сил реакції ґрунту (GRF) на основі моделі динаміки твердого тіла (SRBD).
"""

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class QuadrupedParams:
    mass_kg: float = 12.0                # Маса робота (кг)
    inertia_diag: Tuple[float, float, float] = (0.05, 0.1, 0.1)  # Ixx, Iyy, Izz (кг*м^2)
    gravity: float = 9.81                # Прискорення вільного падіння (м/с^2)
    mu_friction: float = 0.6             # Коефіцієнт тертя лапи з ґрунтом
    f_z_max: float = 160.0               # Максимальна вертикальна сила на лапу (Н)

class ConvexMPCQuadruped:
    def __init__(self, params: QuadrupedParams):
        self.params = params

    def solve_contact_forces(
        self,
        current_pos: List[float],
        current_vel: List[float],
        desired_vel: List[float],
        leg_positions: List[List[float]],
        stance_legs: List[bool]
    ) -> List[List[float]]:
        """
        Розв'язання задачі квазі-MPC для опорних лап.
        Повертає вектори сил [Fx, Fy, Fz] для кожної з 4 лап.
        """
        # Потрібне загальне прискорення корпусу для виходу на desired_vel
        kp_v = 8.0
        kd_v = 4.0
        acc_x = kp_v * (desired_vel[0] - current_vel[0])
        acc_y = kp_v * (desired_vel[1] - current_vel[1])
        acc_z = kp_v * (desired_vel[2] - current_vel[2])

        # Сумарна необхідна сила
        f_total_x = self.params.mass_kg * acc_x
        f_total_y = self.params.mass_kg * acc_y
        f_total_z = self.params.mass_kg * (self.params.gravity + acc_z)

        active_count = sum(stance_legs)
        if active_count == 0:
            return [[0.0, 0.0, 0.0] for _ in range(4)]

        # Розподіл сил по активних лапах
        base_fz = f_total_z / active_count
        base_fx = f_total_x / active_count
        base_fy = f_total_y / active_count

        forces = []
        for i in range(4):
            if not stance_legs[i]:
                forces.append([0.0, 0.0, 0.0])
                continue

            # Обмеження сили конусом тертя Камма
            fz = min(self.params.f_z_max, max(5.0, base_fz))
            max_horiz = self.params.mu_friction * fz

            fx = max(-max_horiz, min(max_horiz, base_fx))
            fy = max(-max_horiz, min(max_horiz, base_fy))
            forces.append([round(fx, 2), round(fy, 2), round(fz, 2)])

        return forces

def main():
    print("================================================================")
    print("ОПУКЛИЙ MPC-КОНТРОЛЕР ДЛЯ ЧОТИРИНОГОГО РОБОТА (QUADRUPED MPC)")
    print("================================================================")
    mpc = ConvexMPCQuadruped(QuadrupedParams())

    # Тротова хода: лапи 0 і 3 в контакті (діагональ 1)
    leg_coords = [
        [0.2, -0.15, 0.0],   # FL
        [0.2, 0.15, 0.0],    # FR
        [-0.2, -0.15, 0.0],  # RL
        [-0.2, 0.15, 0.0]    # RR
    ]
    stance = [True, False, False, True]  # Діагональна опора

    v_cur = [0.2, 0.0, 0.0]
    v_target = [0.8, 0.0, 0.0]

    grf = mpc.solve_contact_forces([0, 0, 0.3], v_cur, v_target, leg_coords, stance)
    print(f"Цільова швидкість: {v_target[0]} м/с, поточна: {v_cur[0]} м/с")
    print("Сили реакції опор (GRF) під лапами:")
    for i, (name, f) in enumerate(zip(["FL", "FR", "RL", "RR"], grf)):
        st = "ОПОРА" if stance[i] else "ПЕРЕНЕСЕННЯ"
        print(f"  Лапа {name} ({st:11s}): Fx = {f[0]:6.2f} Н, Fy = {f[1]:6.2f} Н, Fz = {f[2]:6.2f} Н")
    print("================================================================")

if __name__ == "__main__":
    main()
