"""
worm_winch_safety.py — Інженерний модуль розрахунку геометрії, самогальмування,
ККД, теплового балансу та безпеки черв'ячного приводу вантажопідйомної лебідки.
"""

import math
from dataclasses import dataclass


@dataclass
class WormDriveConfig:
    """Конфігурація черв'ячної передачі та фрикційних властивостей матеріалів."""
    module_mm: float
    z1_starts: int
    z2_teeth: int
    q_diameter_factor: float
    pressure_angle_deg: float = 20.0
    mu_static: float = 0.09
    mu_dynamic: float = 0.035


@dataclass
class SafetyReport:
    """Підсумковий інженерний звіт безпеки та енергетичного балансу приводу."""
    lead_angle_deg: float
    friction_angle_static_deg: float
    friction_angle_dyn_deg: float
    is_statically_self_locking: bool
    dynamic_safety_factor: float
    is_dynamically_safe: bool
    efficiency_direct: float
    efficiency_reverse: float
    heat_loss_watts: float
    required_brake_torque_Nm: float
    summary: str


class WinchSafetyCalculator:
    """Розрахунок умов самогальмування та параметрів безпеки черв'ячної лебідки."""

    def __init__(self, config: WormDriveConfig):
        self.cfg = config
        self.alpha_n = math.radians(config.pressure_angle_deg)

    def lead_angle_rad(self) -> float:
        """Кут підйому витка черв'яка gamma = arctan(z1 / q)."""
        return math.atan(self.cfg.z1_starts / self.cfg.q_diameter_factor)

    def reduced_friction_angle_rad(self, mu: float) -> float:
        """
        Приведений кут тертя з урахуванням клиновидного розпирання зуба:
        tan(phi') = mu' = mu / cos(alpha_n).
        """
        mu_prime = mu / math.cos(self.alpha_n)
        return math.atan(mu_prime)

    def evaluate_winch(
        self,
        load_mass_kg: float,
        drum_radius_m: float,
        hoisting_speed_mps: float = 0.25,
    ) -> SafetyReport:
        """
        Комплексний розрахунок навантаження, перевірка статичного та динамічного
        самогальмування, визначення моменту обов'язкового електромагнітного гальма.
        """
        gamma = self.lead_angle_rad()
        gamma_deg = math.degrees(gamma)

        # Кути тертя: статичний спокою та динамічний ковзання при вібраціях
        phi_static = self.reduced_friction_angle_rad(self.cfg.mu_static)
        phi_dyn = self.reduced_friction_angle_rad(self.cfg.mu_dynamic)

        phi_static_deg = math.degrees(phi_static)
        phi_dyn_deg = math.degrees(phi_dyn)

        # Критерій статичного самогальмування: gamma <= phi'
        is_stat_locked = gamma <= phi_static

        # Динамічний коефіцієнт запасу самогальмування: S_dyn = tan(phi'_dyn) / tan(gamma)
        s_dyn = math.tan(phi_dyn) / math.tan(gamma)
        is_dyn_safe = s_dyn >= 1.25

        # Прямий ККД при підйомі вантажу
        eta_dir = math.tan(gamma) / math.tan(gamma + phi_dyn)

        # Зворотний ККД при спробі провертання від навантаження
        if gamma > phi_dyn:
            eta_rev = math.tan(gamma - phi_dyn) / math.tan(gamma)
        else:
            eta_rev = math.tan(gamma - phi_static) / math.tan(gamma)

        # Силові та енергетичні показники
        g = 9.81
        load_force_N = load_mass_kg * g
        wheel_torque_Nm = load_force_N * drum_radius_m
        ratio = float(self.cfg.z2_teeth) / float(self.cfg.z1_starts)

        # Потужність та теплові втрати в картері
        p_useful_W = load_force_N * hoisting_speed_mps
        p_in_W = p_useful_W / eta_dir if eta_dir > 0 else 0.0
        p_loss_W = p_in_W - p_useful_W

        # Нормативний розрахунок моменту допоміжного електромагнітного гальма на валу черв'яка
        # Коефіцієнт запасу гальмування K_brake = 1.5 згідно з правилами будови кранів
        k_brake = 1.5
        static_back_torque_worm_Nm = wheel_torque_Nm / ratio
        required_brake_torque = k_brake * static_back_torque_worm_Nm

        status_dyn = "ЗАХИЩЕНО (DYN-SAFE)" if is_dyn_safe else "НЕБЕЗПЕКА ЗРИВУ (VIBRATION-RISK)"
        summary = (
            f"Кут витка gamma={gamma_deg:.2f}°, phi_stat={phi_static_deg:.2f}°, phi_dyn={phi_dyn_deg:.2f}°. "
            f"Статичне блокування: {is_stat_locked}. Динамічний запас: S_dyn={s_dyn:.2f} -> {status_dyn}. "
            f"Обов'язкове гальмо T_brake >= {required_brake_torque:.1f} Н*м."
        )

        return SafetyReport(
            lead_angle_deg=gamma_deg,
            friction_angle_static_deg=phi_static_deg,
            friction_angle_dyn_deg=phi_dyn_deg,
            is_statically_self_locking=is_stat_locked,
            dynamic_safety_factor=s_dyn,
            is_dynamically_safe=is_dyn_safe,
            efficiency_direct=eta_dir,
            efficiency_reverse=eta_rev,
            heat_loss_watts=p_loss_W,
            required_brake_torque_Nm=required_brake_torque,
            summary=summary,
        )
