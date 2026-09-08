"""
example.py — Демонстраційний сценарій підбору та перевірки планетарного ступеня
для сервопривода промислового робота-маніпулятора.
"""

from planetary_calculator import PlanetaryGearbox, SynthesisError


def main():
    print("=== Розрахунок прецизійного серворедуктора робота ===")
    
    # Вимоги технічного завдання:
    # Вихідний крутний момент суглоба: T_out = 120 Н*м
    torque_out = 120.0

    # Проектуємо геометрію ступеня:
    # m = 1.5 мм (модуль)
    # z_a = 18 (сонце), z_g = 27 (сателіти), k = 3 сателіти
    # Розрахункова кількість зубів корони: z_b = z_a + 2*z_g = 18 + 54 = 72
    # Перевірка збирання: (18 + 72) / 3 = 90 / 3 = 30 (ділиться націло!)
    try:
        gearbox = PlanetaryGearbox(
            module_mm=1.5,
            z_sun=18,
            z_ring=72,
            z_planet=27,
            num_planets=3,
            face_width_mm=16.0,
            pressure_angle_deg=20.0,
            sigma_F_lim_MPa=480.0,  # Загартована сталь 18ХГТ з цементацією
            sigma_H_lim_MPa=1350.0,
        )
        print("[+] Усі умови монтажу (співвісність, збирання, сусідство) виконано.")
    except SynthesisError as e:
        print(f"[-] Помилка геометрії: {e}")
        return

    # Виконуємо повний розрахунок навантаження
    result = gearbox.evaluate(torque_out_Nm=torque_out)

    print("\n--- Результати інженерного розрахунку ---")
    print(f"Передавальне відношення:      {result.ratio:.2f} : 1")
    print(f"Міжосьова відстань:           {result.center_distance_mm:.2f} мм")
    print(f"Зазор між сателітами:         {result.clearance_satellites_mm:.2f} мм")
    print(f"Згинальне напруження Льюїса:  {result.bending_stress_MPa:.1f} МПа (Запас: {result.safety_factor_bending:.2f})")
    print(f"Контактне напруження Герца:   {result.contact_stress_MPa:.1f} МПа (Запас: {result.safety_factor_contact:.2f})")
    print(f"Оцінка кутового люфту:        {result.backlash_arcmin:.2f} кутових мінут")
    print(f"Зведена інерція до двигуна:   {result.reduced_inertia_kg_m2:.6f} кг·м²")
    print(f"\nПідсумок: {result.summary}")

    # Демонстрація перехоплення некоректного числа зубів
    print("\n--- Тест перевірки захисту від некоректного синтезу ---")
    try:
        # Спроба задати сателіт z_g = 25 замість 27 (порушує умову співвісності)
        bad_box = PlanetaryGearbox(
            module_mm=1.5, z_sun=18, z_ring=72, z_planet=25, num_planets=3, face_width_mm=16.0
        )
    except SynthesisError as e:
        print(f"[+] Захист спрацював коректно: {e}")


if __name__ == "__main__":
    main()
