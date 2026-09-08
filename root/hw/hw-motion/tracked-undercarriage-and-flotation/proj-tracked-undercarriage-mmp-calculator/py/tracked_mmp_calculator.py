#!/usr/bin/env python3
"""
tracked_mmp_calculator.py
Інженерний калькулятор пікового тиску MMP за моделлю Роуленда та оцінки
флотації й занурення гусеничного рушія в слабкі ґрунти (Терамеханіка Беккера).
"""

import math
from dataclasses import dataclass

@dataclass
class TrackedParams:
    mass_kg: float = 14000.0             # Повна маса машини (кг)
    track_width_m: float = 0.45          # Ширина трака b (м)
    ground_contact_len_m: float = 3.6    # Довжина опорної поверхні гусениці L (м)
    num_road_wheels_per_side: int = 5    # Кількість опорних котків на один борт
    road_wheel_diam_m: float = 0.52      # Діаметр опорного котка d (м)
    track_pitch_m: float = 0.14          # Крок трака p (м)

class TrackedMMPCalculator:
    def __init__(self, p: TrackedParams):
        self.p = p
        self.weight_n = p.mass_kg * 9.81

    def calculate_pressures(self):
        """Розрахунок номінального тиску NGP та пікового тиску MMP Роуленда."""
        # Номінальний тиск (ідеальний)
        total_area = 2.0 * self.p.track_width_m * self.p.ground_contact_len_m
        ngp_kpa = (self.weight_n / total_area) / 1000.0

        # Rowland MMP (Mean Maximum Pressure) для опорних котків на жорсткій стрічці:
        # MMP = (0.5 * W) / (n * b * sqrt(d * p))
        n = self.p.num_road_wheels_per_side
        b = self.p.track_width_m
        d = self.p.road_wheel_diam_m
        p = self.p.track_pitch_m

        mmp_kpa = ((0.5 * self.weight_n) / (n * b * math.sqrt(d * p))) / 1000.0
        return round(ngp_kpa, 1), round(mmp_kpa, 1)

    def estimate_sinkage_cm(self, mmp_kpa: float) -> float:
        """Оцінка глибини колії z за моделлю Беккера для вологого суглинку."""
        k_soil = 85.0  # модуль деформації ґрунту (кПа/м^0.7)
        sinkage_m = (mmp_kpa / k_soil) ** (1.0 / 0.7)
        return round(sinkage_m * 100.0, 1)

def main():
    print("================================================================")
    print("РОЗРАХУНОК СЕРЕДНЬОГО МАКСИМАЛЬНОГО ТИСКУ MMP (ТЕОРІЯ РОУЛЕНДА)")
    print("================================================================")
    calc = TrackedMMPCalculator(TrackedParams())
    ngp, mmp = calc.calculate_pressures()
    sinkage = calc.estimate_sinkage_cm(mmp)

    print(f"Маса платформи: {calc.p.mass_kg / 1000.0:.1f} тонн | Котків на борт: {calc.p.num_road_wheels_per_side}")
    print(f"Номінальний середній тиск (NGP): {ngp} кПа")
    print(f"Піковий тиск під котками (MMP):  {mmp} кПа (перевищення у {mmp/ngp:.1f} рази!)")
    print("----------------------------------------------------------------")
    print(f"Розрахункова глибина колії в суглинку: z = {sinkage} см")
    print(f"Критерій прохідності НАТО (MMP < 180 кПа): {'ПРОХІДНИЙ' if mmp <= 180 else 'НЕПРОХІДНИЙ (СІДАЄ НА ДНИЩЕ)'}")
    print("================================================================")

if __name__ == "__main__":
    main()
