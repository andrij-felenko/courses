#!/usr/bin/env python3
"""
foc_qdd_controller.py
Реалізація польоорієнтованого векторного керування (FOC), оцінки крутного моменту
за квадратурним струмом Iq та контуру віртуального механічного імпедансу для QDD-привода.
"""

import math
from typing import Tuple, Dict


class PIDController:
    """Дискретний пропорційно-інтегральний регулятор з обмеженням інтегрального насичення."""

    def __init__(self, kp: float, ki: float, kd: float, output_limit: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limit = output_limit
        self.integral = 0.0
        self.prev_error = 0.0

    def reset(self) -> None:
        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, target: float, actual: float, dt: float) -> float:
        error = target - actual
        self.integral += error * dt

        # Обмеження інтегрального накопичення (anti-windup)
        if self.ki > 0:
            int_limit = self.output_limit / self.ki
            self.integral = max(-int_limit, min(int_limit, self.integral))

        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error

        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        return max(-self.output_limit, min(self.output_limit, output))


class FOCQDDController:
    """
    Контролер квазіпрямого привода: FOC-перетворення струмів, безсенсорна
    оцінка моменту та алгоритм віртуальної пружини-демпфера (імпеданс).
    """

    def __init__(
        self,
        pole_pairs: int = 14,
        torque_constant_kt: float = 0.08,  # Н·м/A
        gear_ratio: float = 6.0,           # передатне відношення QDD
        bus_voltage: float = 24.0          # В
    ):
        self.pole_pairs = pole_pairs
        self.kt = torque_constant_kt
        self.gear_ratio = gear_ratio
        self.bus_voltage = bus_voltage

        # Регулятори струмів Id та Iq
        max_voltage = bus_voltage / math.sqrt(3.0)
        self.pid_id = PIDController(kp=2.5, ki=150.0, kd=0.0, output_limit=max_voltage)
        self.pid_iq = PIDController(kp=2.5, ki=150.0, kd=0.0, output_limit=max_voltage)

    def clarke_transform(self, i_a: float, i_b: float) -> Tuple[float, float]:
        """
        Пряме перетворення Кларка: (i_a, i_b, i_c) -> (i_alpha, i_beta).
        Враховує рівновагу фазних струмів: i_a + i_b + i_c = 0.
        """
        i_alpha = i_a
        i_beta = (1.0 / math.sqrt(3.0)) * i_a + (2.0 / math.sqrt(3.0)) * i_b
        return i_alpha, i_beta

    def park_transform(
        self, i_alpha: float, i_beta: float, theta_elec: float
    ) -> Tuple[float, float]:
        """
        Пряме перетворення Парка: перехід із нерухомої системи (alpha, beta)
        в обертову систему ротора (d, q).
        """
        cos_theta = math.cos(theta_elec)
        sin_theta = math.sin(theta_elec)

        i_d = i_alpha * cos_theta + i_beta * sin_theta
        i_q = -i_alpha * sin_theta + i_beta * cos_theta
        return i_d, i_q

    def inverse_park_transform(
        self, v_d: float, v_q: float, theta_elec: float
    ) -> Tuple[float, float]:
        """
        Зворотне перетворення Парка: (v_d, v_q) -> (v_alpha, v_beta).
        """
        cos_theta = math.cos(theta_elec)
        sin_theta = math.sin(theta_elec)

        v_alpha = v_d * cos_theta - v_q * sin_theta
        v_beta = v_d * sin_theta + v_q * cos_theta
        return v_alpha, v_beta

    def mechanical_to_electrical_angle(self, theta_mech: float) -> float:
        """Перетворення механічного кута ротора в електричний кут."""
        elec_angle = (theta_mech * self.pole_pairs) % (2.0 * math.pi)
        return elec_angle

    def estimate_torque(self, i_q: float) -> float:
        """
        Безсенсорна оцінка вихідного крутного моменту на валу редуктора:
        T_out = K_t * I_q * N_gearbox.
        """
        t_motor = self.kt * i_q
        t_output = t_motor * self.gear_ratio
        return t_output

    def compute_virtual_impedance(
        self,
        theta_target: float,
        theta_actual: float,
        omega_actual: float,
        k_spring: float,
        d_damping: float
    ) -> float:
        """
        Закон віртуального пружинно-демпферного імпедансу:
        T_cmd = K_spring * (theta_target - theta_actual) - D_damping * omega_actual.
        """
        error_pos = theta_target - theta_actual
        t_desired = (k_spring * error_pos) - (d_damping * omega_actual)
        return t_desired

    def step(
        self,
        theta_target: float,
        theta_mech: float,
        omega_mech: float,
        i_a: float,
        i_b: float,
        k_spring: float = 12.0,   # Н·м/рад
        d_damping: float = 0.5,   # Н·м·с/рад
        dt: float = 0.001          # 1 кГц цикл
    ) -> Dict[str, float]:
        """
        Повний крок керування: обчислення імпедансу, вимірювання Iq та розрахунок напруг FOC.
        """
        # 1. Електричний кут ротора
        theta_e = self.mechanical_to_electrical_angle(theta_mech)

        # 2. Прямі перетворення струмів Кларка та Парка
        i_alpha, i_beta = self.clarke_transform(i_a, i_b)
        i_d, i_q = self.park_transform(i_alpha, i_beta, theta_e)

        # 3. Оцінка поточного зовнішнього моменту навантаження
        t_estimated = self.estimate_torque(i_q)

        # 4. Розрахунок бажаного крутного моменту за законом імпедансу
        t_cmd = self.compute_virtual_impedance(
            theta_target, theta_mech, omega_mech, k_spring, d_damping
        )

        # 5. Перерахунок моменту в цільовий струм Iq (Id прагнемо тримати 0)
        i_q_target = t_cmd / (self.kt * self.gear_ratio)
        i_d_target = 0.0

        # 6. PID-регулювання струмів у напруги осі d та q
        v_d_cmd = self.pid_id.update(i_d_target, i_d, dt)
        v_q_cmd = self.pid_iq.update(i_q_target, i_q, dt)

        # 7. Зворотний Парк у напруги нерухомої системи alpha, beta
        v_alpha, v_beta = self.inverse_park_transform(v_d_cmd, v_q_cmd, theta_e)

        return {
            "theta_elec": theta_e,
            "i_d": i_d,
            "i_q": i_q,
            "t_estimated": t_estimated,
            "t_cmd": t_cmd,
            "i_q_target": i_q_target,
            "v_alpha": v_alpha,
            "v_beta": v_beta
        }


if __name__ == "__main__":
    controller = FOCQDDController()
    # Тестовий прогін кроку керування
    res = controller.step(
        theta_target=1.0,
        theta_mech=0.8,
        omega_mech=0.1,
        i_a=1.2,
        i_b=-0.6,
        dt=0.001
    )
    print("FOC QDD Controller step result:")
    for k, v in res.items():
        print(f"  {k}: {v:.4f}")
