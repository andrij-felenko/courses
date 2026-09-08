"""
CCPMSwashplateModel: Кінематичний розрахунок тарілки автомата перекосу.
Підтримує конфігурації CCPM 120°, 140° та 90°, круговий обмежувач
(Swashplate Ring Limiter) та аналіз взаємного впливу каналів (cross-coupling).
"""

import math
from typing import Tuple, Dict, List


class CCPMSwashplateModel:
    """Математична та кінематична модель мікшера автомата перекосу CCPM."""

    def __init__(self, ccpm_type: str = "CCPM_120", arm_length_mm: float = 20.0,
                 max_travel_mm: float = 12.0, ring_limit: float = 1.0) -> None:
        """
        Ініціалізація параметрів автомата перекосу.
        :param ccpm_type: "CCPM_120", "CCPM_140" або "CCPM_90"
        :param arm_length_mm: Радіус качалки сервопривода (мм)
        :param max_travel_mm: Повний робочий лінійний хід тяги (мм)
        :param ring_limit: Радіус кругового обмежувача (0.0 .. 1.0)
        """
        valid_types = ("CCPM_120", "CCPM_140", "CCPM_90")
        if ccpm_type not in valid_types:
            raise ValueError(f"Невідома конфігурація CCPM: {ccpm_type}. Допустимі: {valid_types}")

        self.ccpm_type = ccpm_type
        self.arm_length_mm = float(arm_length_mm)
        self.max_travel_mm = float(max_travel_mm)
        self.ring_limit = float(ring_limit)

    def apply_ring_limiter(self, cyclic_pitch: float, cyclic_roll: float) -> Tuple[float, float]:
        """
        Круговий обмежувач Swashplate Ring Limiter.
        Запобігає механічному заклинюванню тарілки при одночасному відхиленні ручки по діагоналі.
        """
        magnitude = math.sqrt(cyclic_pitch**2 + cyclic_roll**2)
        if magnitude > self.ring_limit and magnitude > 1e-7:
            scale = self.ring_limit / magnitude
            return cyclic_pitch * scale, cyclic_roll * scale
        return cyclic_pitch, cyclic_roll

    def compute_servo_displacements(self, collective: float, cyclic_pitch: float,
                                    cyclic_roll: float) -> Tuple[float, float, float]:
        """
        Розрахунок лінійного переміщення тяг трьох сервоприводів (у мм).
        :param collective: Загальний крок [-1.0 .. 1.0]
        :param cyclic_pitch: Циклічний тангаж [-1.0 .. 1.0]
        :param cyclic_roll: Циклічний крен [-1.0 .. 1.0]
        :return: (s1_mm, s2_mm, s3_mm) для сервоприводів
        """
        coll = max(-1.0, min(1.0, float(collective)))
        pitch, roll = self.apply_ring_limiter(float(cyclic_pitch), float(cyclic_roll))

        half_travel = self.max_travel_mm * 0.5
        c_mm = coll * half_travel
        p_mm = pitch * half_travel
        r_mm = roll * half_travel

        if self.ccpm_type == "CCPM_120":
            # Симетрична схема 120°: S1 (заднє/тангаж), S2 (переднє ліве), S3 (переднє праве)
            sin60 = math.sqrt(3.0) / 2.0  # ~0.866025
            s1 = c_mm + p_mm
            s2 = c_mm - 0.5 * p_mm + sin60 * r_mm
            s3 = c_mm - 0.5 * p_mm - sin60 * r_mm

        elif self.ccpm_type == "CCPM_140":
            # Оптимізована схема 140°: зменшує взаємний вплив тангажу на крен
            cos70 = math.cos(math.radians(70.0))  # ~0.342020
            sin70 = math.sin(math.radians(70.0))  # ~0.939693
            s1 = c_mm + p_mm
            s2 = c_mm - cos70 * p_mm + sin70 * r_mm
            s3 = c_mm - cos70 * p_mm - sin70 * r_mm

        else:  # CCPM_90
            # Прямокутна схема: S1 тангаж, S2/S3 диференційний крен
            s1 = c_mm + p_mm
            s2 = c_mm + r_mm
            s3 = c_mm - r_mm

        return s1, s2, s3

    def linearize_servo_arm(self, linear_travel_mm: float) -> float:
        """
        Тригонометрична лінеаризація ходу качалки сервопривода (арксинусна корекція).
        Повертає необхідний кут повороту вала сервопривода в радіанах:
        alpha = arcsin(delta_z / R_arm)
        """
        ratio = linear_travel_mm / self.arm_length_mm
        clamped_ratio = max(-1.0, min(1.0, ratio))
        return math.asin(clamped_ratio)

    def analyze_cross_coupling(self, grid_steps: int = 10) -> Dict[str, float]:
        """
        Числовий аналіз перехресного зв'язку (cross-coupling):
        перевірка появи паразитного колективного зсуву або перекосу тангаж/крен.
        """
        max_coll_drift = 0.0
        max_asymmetry = 0.0

        for i in range(-grid_steps, grid_steps + 1):
            pitch = i / float(grid_steps)
            for j in range(-grid_steps, grid_steps + 1):
                roll = j / float(grid_steps)
                s1, s2, s3 = self.compute_servo_displacements(0.0, pitch, roll)

                # Ефективний колективний зсув тарілки
                eff_coll = (s1 + s2 + s3) / 3.0
                if abs(eff_coll) > max_coll_drift:
                    max_coll_drift = abs(eff_coll)

                # Симетрія бічних сервоприводів при чистому крені
                if abs(pitch) < 1e-7 and abs(roll) > 1e-7:
                    diff = abs(s2 + s3)  # для симетричних схем s2 та s3 мають бути протилежні
                    if diff > max_asymmetry:
                        max_asymmetry = diff

        return {
            "max_collective_drift_mm": max_coll_drift,
            "max_lateral_asymmetry_mm": max_asymmetry,
            "theoretical_coupling_percent": (max_coll_drift / (self.max_travel_mm * 0.5)) * 100.0
        }
