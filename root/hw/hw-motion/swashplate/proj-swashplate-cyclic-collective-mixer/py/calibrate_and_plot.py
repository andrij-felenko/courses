"""
calibrate_and_plot: Скрипт розрахунку калібрувальних діаграм,
перевірки лінійності та генерації таблиць компенсації для CCPMSwashplateModel.
"""

import math
import sys
from swashplate_model import CCPMSwashplateModel


def run_calibration_report():
    print("=" * 70)
    print("ВЕРИФІКАЦІЯ ТА КАЛІБРУВАННЯ КІНЕМАТИКИ АВТОМАТА ПЕРЕКОСУ (eCCPM)")
    print("=" * 70)

    geometries = ["CCPM_120", "CCPM_140", "CCPM_90"]
    models = {geom: CCPMSwashplateModel(ccpm_type=geom, arm_length_mm=20.0, max_travel_mm=12.0)
              for geom in geometries}

    print("\n1. Порівняння перехресного зв'язку (Cross-Coupling):")
    print(f"{'Геометрія':<12} | {'Макс дрейф шагу (мм)':<22} | {'Асиметрія крену (мм)':<22} | {'Паразитний вплив (%)':<20}")
    print("-" * 82)

    for geom, model in models.items():
        metrics = model.analyze_cross_coupling(grid_steps=20)
        drift = metrics["max_collective_drift_mm"]
        asym = metrics["max_lateral_asymmetry_mm"]
        pct = metrics["theoretical_coupling_percent"]
        print(f"{geom:<12} | {drift:<22.4f} | {asym:<22.4f} | {pct:<20.2f}")

    print("\n2. Калібрувальна таблиця ходу сервоприводів для CCPM 120° (крок 0.5):")
    m120 = models["CCPM_120"]
    print(f"{'Collective':<11} | {'Pitch':<8} | {'Roll':<8} | {'S1 (мм)':<9} | {'S2 (мм)':<9} | {'S3 (мм)':<9} | {'Кут S1 (рад)':<12}")
    print("-" * 75)

    test_points = [
        (0.0,  0.0,  0.0),
        (0.5,  0.0,  0.0),
        (1.0,  0.0,  0.0),
        (0.0,  0.5,  0.0),
        (0.0, -0.5,  0.0),
        (0.0,  0.0,  0.5),
        (0.0,  0.0, -0.5),
        (0.5,  0.5,  0.5),
        (0.0,  0.8,  0.8),  # точка під дією Ring Limiter
    ]

    for coll, pitch, roll in test_points:
        s1, s2, s3 = m120.compute_servo_displacements(coll, pitch, roll)
        angle_s1 = m120.linearize_servo_arm(s1)
        print(f"{coll:<11.2f} | {pitch:<8.2f} | {roll:<8.2f} | {s1:<9.3f} | {s2:<9.3f} | {s3:<9.3f} | {angle_s1:<12.4f}")

    print("\n3. Перевірка роботи кільцевого обмежувача (Swashplate Ring Limiter):")
    pitch_in, roll_in = 0.8, 0.8
    mag_in = math.sqrt(pitch_in**2 + roll_in**2)
    p_lim, r_lim = m120.apply_ring_limiter(pitch_in, roll_in)
    mag_out = math.sqrt(p_lim**2 + r_lim**2)
    print(f"Вхідний діагональний вектор : mag = {mag_in:.4f} (pitch={pitch_in:.2f}, roll={roll_in:.2f})")
    print(f"Вихід після Ring Limiter    : mag = {mag_out:.4f} (pitch={p_lim:.4f}, roll={r_lim:.4f})")
    print(f"Статус лімітування          : {'УСПІШНО ОБМЕЖЕНО ДО 1.0' if abs(mag_out - 1.0) < 1e-6 else 'ПОМИЛКА'}")
    print("=" * 70)


if __name__ == "__main__":
    run_calibration_report()
