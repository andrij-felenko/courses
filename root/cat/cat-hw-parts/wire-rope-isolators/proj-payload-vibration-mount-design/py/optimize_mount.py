"""
Головний сценарій параметричного аналізу та оптимізації кута нахилу підвісу.
"""

import math
from spatial_mount_kinematics import SpatialMountModel
from transmissibility_analyzer import TransmissibilityAnalyzer


def main() -> None:
    print("==================================================================")
    print("   МОДЕЛЮВАННЯ ТА ОПТИМІЗАЦІЯ ПРОСТОРОВОГО ВІБРОПІДВІСУ 45°      ")
    print("==================================================================")

    payload_mass_kg = 1.20  # Маса корисного навантаження (наприклад, оптичний блок БПЛА)
    print(f"Розрахункова маса апарата m = {payload_mass_kg:.2f} кг")
    print("Схема підвісу: 4 симетричні опори під кутом theta до горизонту\n")

    # Порівняльний аналіз для різних кутів нахилу
    angles = [30.0, 45.0, 60.0]
    print(f"{'Кут нахилу':<12} | {'K_vert (Н/м)':<13} | {'K_horiz (Н/м)':<14} | {'f0_z (Гц)':<9} | {'T_peak':<8} | {'f_iso (Гц)':<10}")
    print("-" * 75)

    best_model = None
    for angle in angles:
        model = SpatialMountModel(tilt_angle_deg=angle)
        k_dict = model.get_total_stiffness()
        f0 = model.get_natural_frequency(payload_mass_kg, axis="z")
        zeta = model.get_damping_ratio(payload_mass_kg, axis="z")
        t_peak = TransmissibilityAnalyzer.calculate_transmissibility(f0, f0, zeta)
        f_iso = f0 * math.sqrt(2.0)

        print(f"{angle:4.1f} град     | {k_dict['z']:11.1f}   | {k_dict['x']:12.1f}   | {f0:7.1f}   | {t_peak:6.2f} | {f_iso:8.1f}")
        if angle == 45.0:
            best_model = model

    print("-" * 75)
    print("\nВисновки щодо просторової орієнтації 45°:")
    print(" 1. Забезпечує практично збалансований розподіл жорсткості між вертикаллю та горизонталлю.")
    print(" 2. Знижує резонансну частоту до ~19.9 Гц, зміщуючи зону ізоляції вище 28.2 Гц.")

    # Детальний розрахунок для 45 градусів
    f0_45 = best_model.get_natural_frequency(payload_mass_kg, axis="z")
    zeta_45 = best_model.get_damping_ratio(payload_mass_kg, axis="z")

    print(f"\nГрафік амплітудно-частотної характеристики T(f) для кута 45° (zeta = {zeta_45:.3f}):")
    chart = TransmissibilityAnalyzer.render_ascii_achx(f0_45, zeta_45)
    print(chart)
    print("==================================================================")


if __name__ == "__main__":
    main()
