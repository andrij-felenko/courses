"""
example.py — Демонстраційний розрахунок безпеки черв'ячного приводу
будівельної підйомної лебідки вантажопідйомністю 1000 кг.
"""

from worm_winch_safety import WormDriveConfig, WinchSafetyCalculator


def main():
    print("=== Розрахунок безпеки черв'ячного приводу лебідки ===")

    # Параметри підйомного механізму:
    # Вантаж: 1000 кг, барабан радіусом R = 0.15 м, швидкість v = 0.25 м/с
    load_mass = 1000.0
    drum_radius = 0.15

    # Варіант 1: Однозахідний самогальмівний черв'як (z1 = 1, q = 12)
    cfg_safe = WormDriveConfig(
        module_mm=4.0,
        z1_starts=1,
        z2_teeth=40,
        q_diameter_factor=12.0,
        pressure_angle_deg=20.0,
        mu_static=0.09,
        mu_dynamic=0.035,
    )
    calc_safe = WinchSafetyCalculator(cfg_safe)
    report_safe = calc_safe.evaluate_winch(load_mass, drum_radius)

    print("\n--- Варіант 1: Однозахідний черв'як (z1 = 1, q = 12) ---")
    print(f"Кут підйому витка gamma:          {report_safe.lead_angle_deg:.2f}°")
    print(f"Приведений кут тертя спокою:      {report_safe.friction_angle_static_deg:.2f}°")
    print(f"Приведений кут тертя ковзання:    {report_safe.friction_angle_dyn_deg:.2f}°")
    print(f"Статичне самогальмування:         {report_safe.is_statically_self_locking}")
    print(f"Динамічний коефіцієнт запасу:     {report_safe.dynamic_safety_factor:.2f}")
    print(f"Прямий ККД підйому:               {report_safe.efficiency_direct * 100:.1f}%")
    print(f"Теплові втрати в картері:         {report_safe.heat_loss_watts:.0f} Вт")
    print(f"Момент допоміжного гальма:        {report_safe.required_brake_torque_Nm:.1f} Н·м")
    print(f"Підсумок: {report_safe.summary}")

    # Варіант 2: Двозахідний швидкісний черв'як (z1 = 2, q = 10, несамогальмівний)
    cfg_fast = WormDriveConfig(
        module_mm=4.0,
        z1_starts=2,
        z2_teeth=40,
        q_diameter_factor=10.0,
        pressure_angle_deg=20.0,
        mu_static=0.09,
        mu_dynamic=0.035,
    )
    calc_fast = WinchSafetyCalculator(cfg_fast)
    report_fast = calc_fast.evaluate_winch(load_mass, drum_radius)

    print("\n--- Варіант 2: Двозахідний черв'як (z1 = 2, q = 10) ---")
    print(f"Кут підйому витка gamma:          {report_fast.lead_angle_deg:.2f}°")
    print(f"Статичне самогальмування:         {report_fast.is_statically_self_locking} (ПЕРЕДАЧА ОБОРОТНА!)")
    print(f"Динамічний коефіцієнт запасу:     {report_fast.dynamic_safety_factor:.2f}")
    print(f"Прямий ККД підйому:               {report_fast.efficiency_direct * 100:.1f}%")
    print(f"Момент допоміжного гальма:        {report_fast.required_brake_torque_Nm:.1f} Н·м")
    print(f"Підсумок: {report_fast.summary}")


if __name__ == "__main__":
    main()
