#!/usr/bin/env python3
"""
gear_fatigue_calculator.py
Інженерний калькулятор втомного ресурсу зубчастої пари за стандартом ISO 6336.
Розрахунок контактної витривалості (пітинг) та згинальної міцності ніжки зуба.
"""

import math
from dataclasses import dataclass

@dataclass
class GearPairParams:
    normal_module_mm: float = 3.0       # Нормальний модуль m_n (мм)
    teeth_pinion: int = 19              # Кількість зубів шестерні z1
    teeth_wheel: int = 76               # Кількість зубів колеса z2
    face_width_mm: float = 35.0         # Робоча ширина вінця b (мм)
    helix_angle_deg: float = 12.0       # Кут нахилу лінії зуба beta
    pressure_angle_deg: float = 20.0    # Кут профілю alpha_n
    torque_pinion_nm: float = 180.0     # Крутний момент на шестерні T1 (Н*м)
    speed_rpm: float = 1450.0           # Частота обертання шестерні n1 (об/хв)
    hardness_hrc: float = 60.0          # Твердість поверхні (цементація)

class GearFatigueCalculator:
    def __init__(self, p: GearPairParams):
        self.p = p
        self.u = p.teeth_wheel / p.teeth_pinion
        beta_rad = math.radians(p.helix_angle_deg)
        # Ділильні діаметри
        self.d1_mm = (p.normal_module_mm * p.teeth_pinion) / math.cos(beta_rad)
        self.d2_mm = (p.normal_module_mm * p.teeth_wheel) / math.cos(beta_rad)
        # Тангенціальна сила
        self.f_t = (2000.0 * p.torque_pinion_nm) / self.d1_mm

    def calculate_contact_stress(self) -> float:
        """Контактне напруження Герца за ISO 6336 (Method B) [МПа]."""
        z_e = 189.8  # коефіцієнт пружності для сталі (МПа^0.5)
        z_h = 2.45   # коефіцієнт зони зачеплення
        z_eps = 0.85 # коефіцієнт перекриття
        z_beta = math.sqrt(math.cos(math.radians(self.p.helix_angle_deg)))

        # Розрахунок за ISO 6336-2
        w_t = self.f_t / self.p.face_width_mm
        sigma_h0 = z_h * z_e * z_eps * z_beta * math.sqrt((w_t / self.d1_mm) * ((self.u + 1.0) / self.u))
        k_v = 1.12   # динамічний коефіцієнт
        k_a = 1.25   # коефіцієнт режиму навантаження
        k_h = 1.15   # розподіл навантаження по ширині

        return sigma_h0 * math.sqrt(k_a * k_v * k_h)

    def calculate_bending_stress(self) -> float:
        """Напруження згину в ніжці зуба за Льюїсом / ISO 6336-3 [МПа]."""
        y_f = 2.65   # коефіцієнт форми зуба
        y_s = 1.62   # коефіцієнт концентрації напружень у галтелі
        y_beta = 1.0 - (self.p.helix_angle_deg / 120.0)

        k_v = 1.12
        k_a = 1.25
        k_f = 1.18

        sigma_f0 = (self.f_t / (self.p.face_width_mm * self.p.normal_module_mm)) * y_f * y_s * y_beta
        return sigma_f0 * k_a * k_v * k_f

def main():
    print("================================================================")
    print("РОЗРАХУНОК ВТОМНОЇ МІЦНОСТІ ЗУБЧАСТОЇ ПАРИ ЗА ISO 6336")
    print("================================================================")
    calc = GearFatigueCalculator(GearPairParams())
    sigma_h = calc.calculate_contact_stress()
    sigma_f = calc.calculate_bending_stress()

    # Допустимі напруження для цементованої сталі 20ХН3А (60 HRC)
    sigma_h_lim = 1500.0  # МПа
    sigma_f_lim = 480.0   # МПа

    s_h = sigma_h_lim / sigma_h
    s_f = sigma_f_lim / sigma_f

    print(f"Тангенціальна сила F_t: {calc.f_t:.1f} Н")
    print(f"Контактне напруження Герца sigma_H: {sigma_h:.1f} МПа (границя {sigma_h_lim} МПа)")
    print(f"Коефіцієнт запасу за пітингом S_H: {s_h:.2f} (норма >= 1.20) -> {'OK' if s_h >= 1.2 else 'FAIL'}")
    print("----------------------------------------------------------------")
    print(f"Згинальне напруження ніжки sigma_F: {sigma_f:.1f} МПа (границя {sigma_f_lim} МПа)")
    print(f"Коефіцієнт запасу за зламом S_F:   {s_f:.2f} (норма >= 1.40) -> {'OK' if s_f >= 1.4 else 'FAIL'}")
    print("================================================================")

if __name__ == "__main__":
    main()
