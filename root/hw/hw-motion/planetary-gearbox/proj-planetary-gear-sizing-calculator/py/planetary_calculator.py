"""
planetary_calculator.py — Інженерний модуль проектування та розрахунку міцності
одноступеневого планетарного редуктора за схемою 2K-H (із зафіксованою короною).
"""

import math
from dataclasses import dataclass
from typing import Dict, Any


class SynthesisError(ValueError):
    """Помилка геометричного синтезу або порушення умов монтажу ряду."""
    pass


@dataclass
class SynthesisResult:
    """Результати геометричного, міцнісного та динамічного розрахунку ступеня."""
    ratio: float
    center_distance_mm: float
    clearance_satellites_mm: float
    bending_stress_MPa: float
    safety_factor_bending: float
    contact_stress_MPa: float
    safety_factor_contact: float
    backlash_arcmin: float
    reduced_inertia_kg_m2: float
    is_valid: bool
    summary: str


class PlanetaryGearbox:
    """
    Модель планетарного ряду із зафіксованим коронним колесом (тип 2K-H).
    Вхідний вал — сонце (a), вихідний вал — водило (h), нерухома ланка — корона (b).
    """

    def __init__(
        self,
        module_mm: float,
        z_sun: int,
        z_ring: int,
        z_planet: int,
        num_planets: int,
        face_width_mm: float,
        pressure_angle_deg: float = 20.0,
        sigma_F_lim_MPa: float = 450.0,
        sigma_H_lim_MPa: float = 1200.0,
        E_modulus_MPa: float = 2.06e5,
    ):
        self.m = float(module_mm)
        self.z_a = int(z_sun)
        self.z_b = int(z_ring)
        self.z_g = int(z_planet)
        self.k = int(num_planets)
        self.b = float(face_width_mm)
        self.alpha = math.radians(pressure_angle_deg)
        self.sigma_F_lim = float(sigma_F_lim_MPa)
        self.sigma_H_lim = float(sigma_H_lim_MPa)
        self.E = float(E_modulus_MPa)

        # Валідація геометрії при створенні
        self.validate_kinematics()

    def validate_kinematics(self) -> None:
        """Перевіряє три обов'язкові умови синтезу планетарної передачі."""
        # 1. Умова співвісності: радіуси сонце-сателіт та сателіт-корона мають збігатися
        if self.z_b != self.z_a + 2 * self.z_g:
            raise SynthesisError(
                f"Порушено умову співвісності: z_b ({self.z_b}) != z_a ({self.z_a}) + 2*z_g ({2 * self.z_g})."
            )

        # 2. Умова правильного збирання: сума зубів ділиться націло на число сателітів
        if (self.z_a + self.z_b) % self.k != 0:
            raise SynthesisError(
                f"Порушено умову збирання: (z_a + z_b) = {self.z_a + self.z_b} не ділиться на k = {self.k} націло."
            )

        # 3. Умова сусідства: сателіти не повинні торкатися вершинами зубів
        a_w = self.center_distance()
        d_ag = self.m * (self.z_g + 2.0)
        pin_dist = 2.0 * a_w * math.sin(math.pi / self.k)
        clearance = pin_dist - d_ag
        if clearance <= 0:
            raise SynthesisError(
                f"Порушено умову сусідства: зазор між сателітами {clearance:.2f} мм <= 0 (зіткнення зубів)."
            )

    def gear_ratio(self) -> float:
        """Передавальне відношення i_ah при зафіксованій коронній шестерні."""
        return 1.0 + float(self.z_b) / float(self.z_a)

    def center_distance(self) -> float:
        """Міжосьова відстань a_w між сонцем та сателітом (мм)."""
        return self.m * (self.z_a + self.z_g) / 2.0

    def calculate_stresses(
        self, torque_out_Nm: float, load_sharing_factor: float = 1.15
    ) -> Dict[str, float]:
        """
        Розрахунок згинальних напружень у ніжці зуба за Льюїсом
        та контактних напружень за Герцом на найбільш навантаженому сонці.
        """
        ratio = self.gear_ratio()
        t_sun_Nm = torque_out_Nm / ratio

        d_a_mm = self.m * self.z_a
        d_a_m = d_a_mm / 1000.0

        f_t_total_N = (2.0 * t_sun_Nm) / d_a_m
        f_t_sat_N = (f_t_total_N / self.k) * load_sharing_factor

        y_f = 0.40
        sigma_f = (f_t_sat_N * y_f) / (self.b * self.m)

        u = float(self.z_g) / float(self.z_a)
        z_h = 2.495
        z_e = 189.8
        w_t = f_t_sat_N / self.b

        sigma_h = z_h * z_e * math.sqrt((w_t / d_a_mm) * ((u + 1.0) / u))

        return {
            "f_t_sat_N": f_t_sat_N,
            "sigma_F_MPa": sigma_f,
            "safety_F": self.sigma_F_lim / sigma_f if sigma_f > 0 else float("inf"),
            "sigma_H_MPa": sigma_h,
            "safety_H": self.sigma_H_lim / sigma_h if sigma_h > 0 else float("inf"),
        }

    def calculate_backlash_arcmin(self, radial_play_mm: float = 0.035) -> float:
        """Оцінка сумарного кутового люфту на вихідному валу (кутові мінути)."""
        d_b_mm = self.m * self.z_b
        j_rad = (2.0 * radial_play_mm * math.tan(self.alpha)) / d_b_mm
        return j_rad * (180.0 * 60.0 / math.pi)

    def calculate_equivalent_inertia(
        self,
        j_load_kg_m2: float,
        j_carrier_kg_m2: float,
        j_sun_kg_m2: float,
        j_planet_kg_m2: float,
    ) -> float:
        """Зведений до вала електродвигуна момент інерції системи (кг*м²)."""
        ratio = self.gear_ratio()
        j_carrier_red = (j_carrier_kg_m2 + j_load_kg_m2) / (ratio**2)
        i_sat = (float(self.z_b) / float(self.z_g)) / ratio
        j_planets_red = self.k * j_planet_kg_m2 * (i_sat**2)
        return j_sun_kg_m2 + j_carrier_red + j_planets_red

    def evaluate(
        self,
        torque_out_Nm: float,
        j_load_kg_m2: float = 0.05,
        j_carrier_kg_m2: float = 0.002,
        j_sun_kg_m2: float = 0.0001,
        j_planet_kg_m2: float = 0.00005,
    ) -> SynthesisResult:
        """Повний комплексний інженерний аналіз ступеня."""
        stresses = self.calculate_stresses(torque_out_Nm)
        ratio = self.gear_ratio()
        a_w = self.center_distance()
        pin_dist = 2.0 * a_w * math.sin(math.pi / self.k)
        d_ag = self.m * (self.z_g + 2.0)
        clearance = pin_dist - d_ag

        backlash = self.calculate_backlash_arcmin()
        j_eq = self.calculate_equivalent_inertia(
            j_load_kg_m2, j_carrier_kg_m2, j_sun_kg_m2, j_planet_kg_m2
        )

        s_f = stresses["safety_F"]
        s_h = stresses["safety_H"]
        is_pass = (s_f >= 1.4) and (s_h >= 1.2)
        status = "ПРИДАТНИЙ (PASS)" if is_pass else "ПЕРЕВАНТАЖЕННЯ (FAIL)"

        summary = (
            f"Планетарний ступінь: i = {ratio:.2f}:1, a_w = {a_w:.2f} мм, "
            f"Запас згину S_F = {s_f:.2f}, Запас контакту S_H = {s_h:.2f} -> {status}"
        )

        return SynthesisResult(
            ratio=ratio,
            center_distance_mm=a_w,
            clearance_satellites_mm=clearance,
            bending_stress_MPa=stresses["sigma_F_MPa"],
            safety_factor_bending=s_f,
            contact_stress_MPa=stresses["sigma_H_MPa"],
            safety_factor_contact=s_h,
            backlash_arcmin=backlash,
            reduced_inertia_kg_m2=j_eq,
            is_valid=is_pass,
            summary=summary,
        )
