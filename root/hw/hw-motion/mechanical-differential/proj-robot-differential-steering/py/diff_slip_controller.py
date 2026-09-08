#!/usr/bin/env python3
"""
diff_slip_controller.py
Детекція буксування коліс провідного моста на базі моделі Аккермана та скінченний
автомат (FSM) активного ШІМ-підблокування електромагнітної муфти диференціала.
"""

import math
from typing import Dict, Any


class DifferentialSlipController:
    """
    Контролер активного блокування диференціала: порівняння швидкостей коліс із моделлю
    повороту Аккермана, скінченний автомат режимів зчеплення та температурний захист дисків.
    """

    # Стани скінченного автомата (FSM)
    STATE_OPEN = "OPEN"
    STATE_PARTIAL = "PARTIAL_LOCK"
    STATE_LOCKED = "FULL_LOCK"
    STATE_THERMAL = "THERMAL_PROTECTION"

    def __init__(
        self,
        wheelbase: float = 1.2,      # колісна база шасі робота (м)
        track_width: float = 0.8,    # колія моста (м)
        wheel_radius: float = 0.15,  # радіус колеса (м)
        thermal_timeout: float = 10.0  # час до активації термозахисту при безперервному буксуванні (с)
    ):
        self.wheelbase = wheelbase
        self.track = track_width
        self.radius = wheel_radius
        self.thermal_timeout = thermal_timeout

        self.current_state = self.STATE_OPEN
        self.slip_timer = 0.0
        self.pwm_duty = 0.0

    def compute_ackermann_difference(
        self, v_vehicle: float, steering_angle: float
    ) -> float:
        """
        Розрахунок теоретичної різниці кутових швидкостей півосей (omega_L - omega_R)
        для штатного кінематичного повороту Аккермана без проковзування.
        """
        if abs(steering_angle) < 1e-4:
            return 0.0

        # Радіус повороту центру заднього моста: R = L / tg(delta)
        r_turn = self.wheelbase / math.tan(steering_angle)

        # Кутова швидкість повороту корпусу навколо миттєвого центру: omega_z = v / R
        omega_yaw = v_vehicle / r_turn

        # Різниця швидкостей між лівим і правим колесами: Delta_omega = (omega_yaw * B) / r_wheel
        delta_omega_expected = (omega_yaw * self.track) / self.radius
        return delta_omega_expected

    def compute_slip_ratio(
        self,
        omega_left: float,
        omega_right: float,
        delta_expected: float
    ) -> float:
        """
        Розрахунок відносного коефіцієнта некінематичного прослизання (буксування):
        Slip = |(omega_L - omega_R) - Delta_expected| / max(|omega_avg|, 0.1).
        """
        actual_diff = omega_left - omega_right
        kinematic_error = abs(actual_diff - delta_expected)
        avg_speed = max(abs(omega_left + omega_right) * 0.5, 0.1)

        slip_ratio = kinematic_error / avg_speed
        return slip_ratio

    def step(
        self,
        omega_left: float,      # рад/с
        omega_right: float,     # рад/с
        steering_angle: float,  # рад
        v_vehicle: float,       # м/с
        abs_active: bool = False,
        dt: float = 0.01        # крок дискретизації (100 Гц)
    ) -> Dict[str, Any]:
        """
        Виконання одного такту детекції пробуксовки та перемикання станів муфти.
        """
        # 1. Якщо спрацювала система ABS — блокування негайно вимикається
        if abs_active:
            self.current_state = self.STATE_OPEN
            self.pwm_duty = 0.0
            self.slip_timer = 0.0
            return {
                "state": self.current_state,
                "slip_ratio": 0.0,
                "pwm_duty": self.pwm_duty,
                "note": "ABS override: clutch released"
            }

        # 2. Кінематичний аналіз руху
        delta_expected = self.compute_ackermann_difference(v_vehicle, steering_angle)
        slip = self.compute_slip_ratio(omega_left, omega_right, delta_expected)

        # 3. Таймер тривалого буксування для теплового захисту
        if slip >= 0.15:
            self.slip_timer += dt
        else:
            self.slip_timer = max(0.0, self.slip_timer - dt * 2.0)

        # 4. Логіка переходів скінченного автомата (FSM)
        if self.slip_timer > self.thermal_timeout:
            self.current_state = self.STATE_THERMAL
            self.pwm_duty = 0.15  # знижений струм для запобігання спалювання фрикціонів
        else:
            if slip < 0.10:
                self.current_state = self.STATE_OPEN
                self.pwm_duty = 0.0
            elif slip < 0.30:
                self.current_state = self.STATE_PARTIAL
                # Лінійне наростання ШІМ від 20% до 70%
                norm = (slip - 0.10) / 0.20
                self.pwm_duty = 0.20 + 0.50 * norm
            else:
                self.current_state = self.STATE_LOCKED
                self.pwm_duty = 1.0  # 100% соленоїд утримує повне змикання

        return {
            "state": self.current_state,
            "slip_ratio": slip,
            "pwm_duty": self.pwm_duty,
            "delta_expected": delta_expected,
            "slip_timer": self.slip_timer
        }


if __name__ == "__main__":
    controller = DifferentialSlipController()
    # Тестовий сценарій: прямий рух зі зривом правого колеса на льоду
    print("Імітація пробуксовки колеса на слизькій поверхні:")
    for t in range(5):
        res = controller.step(
            omega_left=20.0,
            omega_right=35.0,  # забігання буксуючого колеса
            steering_angle=0.0,
            v_vehicle=3.0,
            dt=0.1
        )
        print(f"t={t*0.1:.1f}s | Стан: {res['state']:<18} | Slip: {res['slip_ratio']:.2f} | PWM: {res['pwm_duty']*100:.0f}%")
