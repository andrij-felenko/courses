#!/usr/bin/env python3
"""
roller_screw_calculator.py
Інженерний розрахунок планетарної роликогвинтової передачі (ШРВП):
контактні напруження Герца, динамічна вантажопідйомність C_dyn та довговічність L10.
"""

import math
import sys
from dataclasses import dataclass
from typing import Tuple

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

@dataclass
class RollerScrewParams:
    screw_diameter_mm: float = 30.0     # Номінальний діаметр гвинта d_0 (мм)
    lead_mm: float = 5.0                # Крок/хід різьби p (мм)
    roller_diameter_mm: float = 10.0    # Діаметр різьбового ролика d_r (мм)
    num_rollers: int = 10               # Кількість роликів у гайці (стандарт 8-12)
    contact_angle_deg: float = 45.0     # Кут профілю нарізки (градуси)
    axial_load_n: float = 15000.0       # Робоче осьове навантаження F_axial (Н)
    speed_rpm: float = 1200.0           # Частота обертання (об/хв)

class RollerScrewCalculator:
    def __init__(self, p: RollerScrewParams):
        self.p = p
        # Число точок одночасного контакту роликів з гвинтом
        self.total_contacts = p.num_rollers * int(p.screw_diameter_mm / p.lead_mm * 2)

    def calculate_hertz_stress(self) -> float:
        """Розрахунок лінійного контактного напруження за Герцом [МПа]."""
        e_modulus = 2.1e5  # Модуль пружності сталі (МПа)
        r_eff = (self.p.roller_diameter_mm / 2.0) * 0.8
        f_per_roller = self.p.axial_load_n / (self.p.num_rollers * math.sin(math.radians(self.p.contact_angle_deg)))

        # Лінійний контакт: sigma_H = sqrt(F * E / (pi * L * R_eff))
        contact_len = 3.0  # ефективна довжина лінії контакту витка (мм)
        sigma_h = math.sqrt((f_per_roller * e_modulus) / (math.pi * contact_len * r_eff))
        return sigma_h

    def dynamic_load_rating(self) -> float:
        """Базова динамічна вантажопідйомність C_dyn [кН]."""
        # Емпірична формула розрахунку C_dyn для ШРВП за ISO 3408
        c_dyn_kn = 0.05 * (self.p.screw_diameter_mm ** 1.4) * (self.p.num_rollers ** 0.7)
        return round(c_dyn_kn, 1)

    def calculate_l10_life(self) -> Tuple[float, float]:
        """Розрахунок ресурсу довговічності L10 (млн обертів та мотогодин)."""
        c_dyn_n = self.dynamic_load_rating() * 1000.0
        # Для роликових тіл кочення показник ступеня p = 10/3 (3.333)
        p_exp = 10.0 / 3.0
        l10_rev_million = (c_dyn_n / self.p.axial_load_n) ** p_exp
        l10_hours = (l10_rev_million * 1e6) / (60.0 * self.p.speed_rpm)
        return l10_rev_million, l10_hours

def main():
    params = RollerScrewParams()
    calc = RollerScrewCalculator(params)

    sigma_h = calc.calculate_hertz_stress()
    c_dyn = calc.dynamic_load_rating()
    l10_rev, l10_h = calc.calculate_l10_life()

    print('================================================================')
    print('ІНЖЕНЕРНИЙ РОЗРАХУНОК РОЛИКОГВИНТОВОЇ ПЕРЕДАЧІ (ШРВП)')
    print('================================================================')
    print(f'Діаметр гвинта: {params.screw_diameter_mm} мм | Крок різьби: {params.lead_mm} мм')
    print(f'Кількість роликів: {params.num_rollers} | Сумарно точок контакту: {calc.total_contacts}')
    print(f'Робоче осьове зусилля: {params.axial_load_n:.0f} Н | Швидкість: {params.speed_rpm} об/хв')
    print('----------------------------------------------------------------')
    print(f'Контактні напруження за Герцом: {sigma_h:.1f} МПа (допустимо: < 1600 МПа)')
    print(f'Динамічна вантажопідйомність C_dyn: {c_dyn:.1f} кН')
    print(f'Розрахунковий ресурс L10: {l10_rev:.1f} млн обертів ({l10_h:.0f} мотогодин)')
    print('================================================================')

if __name__ == '__main__':
    main()
