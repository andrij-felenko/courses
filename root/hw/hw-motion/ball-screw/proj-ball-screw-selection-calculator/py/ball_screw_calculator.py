#!/usr/bin/env python3
"""
ball_screw_calculator.py
Модульний інженерний калькулятор для вибору, перевірки та теплового аналізу
кульково-гвинтових передач (ШВП) за стандартом ISO 3408.
"""

import math
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class LoadStep:
    """Одиничний крок робочого циклу навантаження осі верстата."""
    force_n: float       # Осьова сила (сила різання + інерція), Н
    speed_rpm: float     # Швидкість обертання гвинта, об/хв
    time_fraction: float # Частка часу кроку в загальному циклі (0.0 .. 1.0)


@dataclass
class BallScrewGeometry:
    """Геометричні та механічні параметри кулькового гвинта."""
    nominal_diameter_mm: float  # Номінальний діаметр d, мм
    root_diameter_mm: float     # Внутрішній діаметр різьби dr, мм
    lead_mm: float              # Крок різьби Ph, мм
    length_unsupported_mm: float # Робоча безопорна довжина гвинта L, мм
    dynamic_load_rating_ca_n: float # Базова динамічна вантажопідйомність Ca, Н
    youngs_modulus_mpa: float = 2.06e5  # Модуль пружності сталі E, МПа (Н/мм²)
    linear_expansion_coeff: float = 1.17e-5  # Коефіцієнт теплового розширення α, 1/°C


class MountingScheme:
    """Коефіцієнти схем монтажу опорних підшипників ШВП."""
    FIXED_FREE = {"name": "Фіксована - Вільна", "fk": 0.25, "fc": 0.45}
    FIXED_SUPPORTED = {"name": "Фіксована - Плаваюча (Оперта)", "fk": 2.05, "fc": 3.92}
    FIXED_FIXED = {"name": "Фіксована - Фіксована", "fk": 4.00, "fc": 5.99}


class BallScrewCalculator:
    """
    Інженерний калькулятор ШВП за стандартом ISO 3408:
    розрахунок ресурсу L_10, критичних обертів, стійкості Ейлера та теплового натягу.
    """

    def __init__(self, geometry: BallScrewGeometry, mounting: Dict[str, float]):
        self.geo = geometry
        self.mounting = mounting

    def compute_equivalent_load_and_speed(
        self, cycle: List[LoadStep]
    ) -> Tuple[float, float]:
        """
        Обчислення еквівалентного динамічного осьового навантаження Fm
        та еквівалентної швидкості nm за стандартом ISO 3408.
        """
        total_time = sum(step.time_fraction for step in cycle)
        if not math.isclose(total_time, 1.0, rel_tol=1e-3):
            raise ValueError(f"Сума часток часу циклу має дорівнювати 1.0, отримано: {total_time}")

        # Еквівалентна швидкість: nm = sum(ni * qi)
        n_m = sum(step.speed_rpm * step.time_fraction for step in cycle)

        # Еквівалентна сила: Fm = (sum(Fi^3 * ni * qi) / nm)^(1/3)
        weighted_force_sum = sum(
            (step.force_n ** 3) * step.speed_rpm * step.time_fraction
            for step in cycle
        )
        if n_m > 0:
            f_m = (weighted_force_sum / n_m) ** (1.0 / 3.0)
        else:
            f_m = 0.0

        return f_m, n_m

    def compute_life_rating(
        self, f_equivalent_n: float, n_equivalent_rpm: float
    ) -> Dict[str, float]:
        """
        Розрахунок номінальної довговічності L_10 у мільйонах обертів
        та годинах безперервної роботи L_10h.
        """
        if f_equivalent_n <= 0:
            return {"l10_rev_millions": float("inf"), "l10_hours": float("inf")}

        # L_10 = (Ca / Fm)^3 (у мільйонах обертів, тобто одиниці 10^6)
        l10_millions = (self.geo.dynamic_load_rating_ca_n / f_equivalent_n) ** 3.0

        # L10h = (L10 * 10^6) / (60 * nm)
        if n_equivalent_rpm > 0:
            l10_hours = (l10_millions * 1e6) / (60.0 * n_equivalent_rpm)
        else:
            l10_hours = float("inf")

        return {
            "l10_rev_millions": l10_millions,
            "l10_hours": l10_hours
        }

    def compute_critical_speed_rpm(self) -> Dict[str, float]:
        """
        Розрахунок критичної швидкості обертання nc для запобігання резонансному биттю
        та допустимої робочої швидкості з коефіцієнтом безпеки 0.8.
        """
        fc = self.mounting["fc"]
        dr = self.geo.root_diameter_mm
        l_len = self.geo.length_unsupported_mm

        # Стандартна інженерна формула: nc = fc * (dr / L^2) * 10^7, об/хв
        n_critical = fc * (dr / (l_len ** 2)) * 1.0e7
        n_permissible = 0.8 * n_critical

        # Перевірка обмеження за швидкісним фактором d * n (типово d*n <= 70000..100000)
        dn_limit_rpm = 70000.0 / self.geo.nominal_diameter_mm

        return {
            "n_critical_rpm": n_critical,
            "n_permissible_rpm": min(n_permissible, dn_limit_rpm),
            "dn_limit_rpm": dn_limit_rpm
        }

    def compute_euler_buckling_load_n(self) -> Dict[str, float]:
        """
        Розрахунок граничного осьового стискального навантаження за стійкістю Ейлера
        та допустимого зусилля з коефіцієнтом безпеки S = 2.5.
        """
        fk = self.mounting["fk"]
        dr = self.geo.root_diameter_mm
        l_len = self.geo.length_unsupported_mm

        # Формула Ейлера для ШВП: Pk = fk * (dr^4 / L^2) * 10^4, Н
        p_critical = fk * ((dr ** 4) / (l_len ** 2)) * 1.0e4
        safety_factor = 2.5
        p_permissible = p_critical / safety_factor

        return {
            "p_critical_n": p_critical,
            "p_permissible_n": p_permissible,
            "safety_factor": safety_factor
        }

    def compute_thermal_elongation_and_prestretch(
        self, delta_temp_c: float
    ) -> Dict[str, float]:
        """
        Розрахунок температурного подовження гвинта ΔL та необхідного зусилля
        механічного попереднього розтягу (pre-stretch) для його компенсації.
        """
        l_len = self.geo.length_unsupported_mm
        dr = self.geo.root_diameter_mm
        alpha = self.geo.linear_expansion_coeff
        e_mod = self.geo.youngs_modulus_mpa

        # Температурне подовження: ΔL = α * L * ΔT, мм
        delta_l_mm = alpha * l_len * delta_temp_c

        # Площа поперечного перерізу сердечника гвинта: A = π * dr² / 4, мм²
        area_mm2 = (math.pi * (dr ** 2)) / 4.0

        # Зусилля попереднього розтягу: F_stretch = ΔL * E * A / L = α * ΔT * E * A, Н
        f_prestretch_n = alpha * delta_temp_c * e_mod * area_mm2

        return {
            "delta_l_microns": delta_l_mm * 1000.0,
            "f_prestretch_n": f_prestretch_n,
            "core_area_mm2": area_mm2
        }


def main():
    """Демонстрація розрахунку ШВП для вертикальної осі фрезерного верстата з ЧПК."""
    # Параметри гвинта HIWIN R25-05 (d=25 мм, крок=5 мм, dr=21.4 мм, Ca=14.2 кН, L=800 мм)
    geometry = BallScrewGeometry(
        nominal_diameter_mm=25.0,
        root_diameter_mm=21.4,
        lead_mm=5.0,
        length_unsupported_mm=800.0,
        dynamic_load_rating_ca_n=14200.0
    )

    # Схема закріплення: Фіксована - Плаваюча
    calc = BallScrewCalculator(geometry, MountingScheme.FIXED_SUPPORTED)

    # Робочий цикл обробки: прискорення, різання, швидке повернення
    duty_cycle = [
        LoadStep(force_n=4200.0, speed_rpm=600.0, time_fraction=0.15),  # Розгін
        LoadStep(force_n=2800.0, speed_rpm=1200.0, time_fraction=0.60), # Фрезерування
        LoadStep(force_n=1200.0, speed_rpm=2400.0, time_fraction=0.25)  # Холостий хід
    ]

    # 1. Еквівалентне навантаження
    fm, nm = calc.compute_equivalent_load_and_speed(duty_cycle)
    print("=== Результати розрахунку ШВП (ISO 3408) ===")
    print(f"Еквівалентне навантаження Fm: {fm:.1f} Н")
    print(f"Еквівалентна швидкість nm:   {nm:.1f} об/хв")

    # 2. Довговічність
    life = calc.compute_life_rating(fm, nm)
    print(f"Ресурс L10:                 {life['l10_rev_millions']:.2f} млн обертів")
    print(f"Ресурс у годинах L10h:      {life['l10_hours']:.0f} годин")

    # 3. Критична швидкість биття
    speed_check = calc.compute_critical_speed_rpm()
    print(f"Критична швидкість биття:   {speed_check['n_critical_rpm']:.0f} об/хв")
    print(f"Допустима швидкість:        {speed_check['n_permissible_rpm']:.0f} об/хв")

    # 4. Стійкість Ейлера
    buckling = calc.compute_euler_buckling_load_n()
    print(f"Критична сила Ейлера Pk:    {buckling['p_critical_n']:.1f} Н")
    print(f"Допустима осьова сила:      {buckling['p_permissible_n']:.1f} Н")

    # 5. Температурне подовження (+5 °C нагрів)
    thermal = calc.compute_thermal_elongation_and_prestretch(delta_temp_c=5.0)
    print(f"Подовження при нагріві +5C: {thermal['delta_l_microns']:.1f} мкм")
    print(f"Зусилля розтягу витяжки:    {thermal['f_prestretch_n']:.1f} Н")


if __name__ == "__main__":
    main()
