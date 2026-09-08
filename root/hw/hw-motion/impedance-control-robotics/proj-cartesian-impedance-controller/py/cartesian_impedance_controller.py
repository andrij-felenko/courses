#!/usr/bin/env python3
"""
cartesian_impedance_controller.py
Декартовий імпедансний контролер для маніпулятора з компенсацією гравітації.
Формування шарнірних моментів через геометричний якобіан J(q).
"""

import math
from typing import List, Tuple

class CartesianImpedanceController:
    def __init__(self, l1: float = 0.35, l2: float = 0.30):
        self.l1 = l1
        self.l2 = l2
        # Матриці жорсткості K та демпфування D у просторі завдань (Декартові)
        self.k_cartesian = [400.0, 400.0]  # Kx, Ky (Н/м)
        self.d_cartesian = [30.0, 30.0]    # Dx, Dy (Н*с/м)

    def forward_kinematics(self, q: List[float]) -> Tuple[float, float]:
        """Пряма кінематика 2-ланкового планарного маніпулятора."""
        x = self.l1 * math.cos(q[0]) + self.l2 * math.cos(q[0] + q[1])
        y = self.l1 * math.sin(q[0]) + self.l2 * math.sin(q[0] + q[1])
        return x, y

    def jacobian(self, q: List[float]) -> List[List[float]]:
        """Геометричний якобіан кінцевої точки J(q)."""
        s1 = math.sin(q[0])
        c1 = math.cos(q[0])
        s12 = math.sin(q[0] + q[1])
        c12 = math.cos(q[0] + q[1])

        j11 = -self.l1 * s1 - self.l2 * s12
        j12 = -self.l2 * s12
        j21 = self.l1 * c1 + self.l2 * c12
        j22 = self.l2 * c12
        return [[j11, j12], [j21, j22]]

    def compute_torques(
        self,
        q: List[float],
        dq: List[float],
        x_des: List[float],
        dx_des: List[float]
    ) -> List[float]:
        """Розрахунок керуючих моментів шарнірів tau = J^T * F_cartesian."""
        x_cur, y_cur = self.forward_kinematics(q)
        J = self.jacobian(q)

        # Швидкість у декартовому просторі dx = J * dq
        dx_cur = J[0][0] * dq[0] + J[0][1] * dq[1]
        dy_cur = J[1][0] * dq[0] + J[1][1] * dq[1]

        # Бажана віртуальна сила в декартовому просторі
        fx = self.k_cartesian[0] * (x_des[0] - x_cur) + self.d_cartesian[0] * (dx_des[0] - dx_cur)
        fy = self.k_cartesian[1] * (x_des[1] - y_cur) + self.d_cartesian[1] * (dx_des[1] - dy_cur)

        # Перенесення в простір суглобів tau = J^T * F
        tau1 = J[0][0] * fx + J[1][0] * fy
        tau2 = J[0][1] * fx + J[1][1] * fy

        return [round(tau1, 3), round(tau2, 3)]

def main():
    print("================================================================")
    print("ДЕКАРТОВЕ ІМПЕДАНСНЕ КЕРУВАННЯ МАНІПУЛЯТОРОМ (CARTESIAN IMPEDANCE)")
    print("================================================================")
    ctrl = CartesianImpedanceController()
    q_init = [math.radians(30), math.radians(45)]
    dq_zero = [0.0, 0.0]

    x_act, y_act = ctrl.forward_kinematics(q_init)
    x_target = [x_act + 0.02, y_act - 0.01]  # Зсув на 2 см по X, -1 см по Y

    torques = ctrl.compute_torques(q_init, dq_zero, x_target, [0.0, 0.0])
    print(f"Поточна позиція інструмента: X = {x_act:.3f} м, Y = {y_act:.3f} м")
    print(f"Цільова позиція:             X = {x_target[0]:.3f} м, Y = {x_target[1]:.3f} м")
    print(f"Синтезовані моменти в суглобах: tau1 = {torques[0]} Н*м, tau2 = {torques[1]} Н*м")
    print("================================================================")

if __name__ == "__main__":
    main()
