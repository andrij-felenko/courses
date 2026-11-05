"""
main.py
Головний виконуваний скрипт та точка входу інтерфейсу командного рядка (CLI).

Забезпечує конфігурацію просторових зсувів плеча Аббе (dy, dz), одиниць виміру кута,
координацію конвеєра зчитування даних лазерного інтерферометра, обчислення цифрової
компенсації, збереження таблиць корекції для систем ЧПУ та генерацію детального
консольного метрологічного звіту.
"""
import argparse
import math
from pathlib import Path
import sys

from abbe_compensator import AbbeArm, AbbeCompensator
from compensation_table import CompensationTable, MetrologyDataError


def generate_sample_interferometer_data(filepath: Path) -> None:
    """
    Генерація реалістичного зразкового файлу замірів інтерферометра,
    якщо вхідний файл ще не створено користувачем.

    Імітує типову геометрію прецизійних напрямних верстата:
    - Хід осі X: 0..500 мм із регулярним кроком 50 мм (11 точок).
    - Тангаж (pitch): дугоподібний прогин під вагою каретки (-3.5 .. +4.8 arcsec).
    - Рискання (yaw): поперечна хвилястість бокової бази напрямної (-2.8 .. +3.1 arcsec).
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    positions = [float(x) for x in range(0, 550, 50)]

    lines = [
        "# Лазерний інтерферометр: кутові заміри тангажу та рискання осі X\n",
        "# Формат: position [мм], pitch [arcsec], yaw [arcsec]\n",
        "# position, pitch, yaw\n",
    ]
    for x in positions:
        # Прогин напрямних уздовж ходу
        pitch = 4.5 * math.sin(math.pi * x / 500.0) - 2.0 * (x / 500.0)
        # Бічний перекіс приводу
        yaw = 3.2 * math.cos(1.5 * math.pi * x / 500.0) - 1.1
        lines.append(f"{x:8.2f}, {pitch:8.3f}, {yaw:8.3f}\n")

    with filepath.open("w", encoding="utf-8") as f:
        f.writelines(lines)


def print_metrology_report(
    arm: AbbeArm,
    unit: str,
    table: CompensationTable,
    step: float,
    test_pos: float,
    interp_corr: float,
    linuxcnc_path: Path,
    fanuc_path: Path,
    csv_path: Path
) -> None:
    """Виведення структурованого метрологічного звіту в консоль."""
    sep = "=" * 74
    subsep = "-" * 74

    print("\n" + sep)
    print(" МЕТРОЛОГІЧНИЙ ЗВІТ: РОЗРАХУНОК ТА ЦИФРОВА КОМПЕНСАЦІЯ ПОХИБКИ АББЕ")
    print(sep)
    print("  1. ГЕОМЕТРІЯ ПЛЕЧА АББЕ ТА ПАРАМЕТРИ ДАВАЧА:")
    print(f"     * Зсув по осі Y (dy)         : {arm.dy:8.2f} мм (вплив на рискання/yaw)")
    print(f"     * Зсув по осі Z (dz)         : {arm.dz:8.2f} мм (вплив на тангаж/pitch)")
    print(f"     * Зсув по осі X (dx)         : {arm.dx:8.2f} мм")
    print(f"     * Вхідні кутові одиниці      : {unit}")
    print(subsep)
    print("  2. ПАРАМЕТРИ КАЛІБРУВАЛЬНОЇ СІТКИ:")
    start_pos, end_pos = table.travel_range
    print(f"     * Діапазон ходу осі X       : {start_pos:.2f} .. {end_pos:.2f} мм (довжина: {end_pos - start_pos:.2f} мм)")
    print(f"     * Крок сітки (grid step)     : {step:.4f} мм (стабільний, перевірено)")
    print(f"     * Кількість вузлів сітки     : {table.count} точок")
    print(subsep)
    print("  3. ОЦІНКА ПОХИБКИ АББЕ (ВЗДОВЖ ОСІ X):")
    print(f"     * Максимальне зміщення (+E)  : {table.max_error_um:+8.3f} мкм")
    print(f"     * Мінімальне зміщення (-E)  : {table.min_error_um:+8.3f} мкм")
    print(f"     * Повний розмах (Peak-to-Peak: {table.peak_to_peak_um:8.3f} мкм")
    print(f"     * Середньоквадратичне (RMS)  : {table.rms_error_um:8.3f} мкм")
    print(subsep)
    print("  4. ТАБЛИЦЯ КАЛІБРУВАЛЬНИХ ВУЗЛІВ:")
    print(f"     {'Позиція [мм]':>12} | {'Pitch [µrad]':>14} | {'Yaw [µrad]':>14} | {'Похибка [мкм]':>14} | {'Поправка [мкм]':>14}")
    print("     " + "-" * 70)
    for p in table.points:
        pitch_urad = p.pitch_rad * 1e6
        yaw_urad = p.yaw_rad * 1e6
        err_um = p.abbe_error * 1000.0
        corr_um = p.correction * 1000.0
        print(f"     {p.position:12.2f} | {pitch_urad:14.3f} | {yaw_urad:14.3f} | {err_um:+14.3f} | {corr_um:+14.3f}")
    print(subsep)
    print("  5. ПЕРЕВІРКА ІНТЕРПОЛЯЦІЇ В РЕАЛЬНОМУ ЧАСІ:")
    print(f"     * Запитана координата X      : {test_pos:.3f} мм")
    print(f"     * Інтерпольована поправка    : {interp_corr * 1000.0:+8.3f} мкм ({interp_corr:+.6f} мм)")
    print(subsep)
    print("  6. ЗГЕНЕРОВАНІ ФАЙЛИ ДЛЯ СИСТЕМ ЧПУ:")
    print(f"     * LinuxCNC comp file         : {linuxcnc_path}")
    print(f"     * Fanuc pitch compensation   : {fanuc_path}")
    print(f"     * Повний метрологічний CSV   : {csv_path}")
    print(sep + "\n")


def build_parser() -> argparse.ArgumentParser:
    """Побудова парсера аргументів командного рядка."""
    parser = argparse.ArgumentParser(
        description="Розрахунок та цифрова компенсація похибки Аббе на основі замірів лазерного інтерферометра."
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        default="interferometer_data.csv",
        help="Шлях до вхідного файлу замірів інтерферометра (position, pitch, yaw)."
    )
    parser.add_argument(
        "--arm-dy",
        type=float,
        default=150.0,
        help="Зміщення плеча Аббе по осі Y у міліметрах (за замовчуванням: 150.0 мм)."
    )
    parser.add_argument(
        "--arm-dz",
        type=float,
        default=220.0,
        help="Зміщення плеча Аббе по осі Z у міліметрах (за замовчуванням: 220.0 мм)."
    )
    parser.add_argument(
        "--arm-dx",
        type=float,
        default=0.0,
        help="Поздовжній винос плеча Аббе по осі X у міліметрах (за замовчуванням: 0.0 мм)."
    )
    parser.add_argument(
        "-u", "--unit",
        type=str,
        default="arcsec",
        choices=["arcsec", "urad", "µrad", "rad"],
        help="Кутові одиниці виміру у вхідному файлі (arcsec, urad, µrad, rad)."
    )
    parser.add_argument(
        "--out-linuxcnc",
        type=str,
        default="abbe_linuxcnc.comp",
        help="Шлях вихідного файлу таблиці компенсації для LinuxCNC."
    )
    parser.add_argument(
        "--out-fanuc",
        type=str,
        default="abbe_fanuc.dat",
        help="Шлях вихідного файлу крокової компенсації для Fanuc."
    )
    parser.add_argument(
        "--out-csv",
        type=str,
        default="abbe_compensation.csv",
        help="Шлях вихідного CSV-файлу зведених метрологічних даних."
    )
    parser.add_argument(
        "--step-tolerance",
        type=float,
        default=1e-4,
        help="Допуск на рівномірність кроку сітки калібрування в мм (за замовчуванням: 0.0001 мм)."
    )
    parser.add_argument(
        "--test-pos",
        type=float,
        default=175.0,
        help="Тестова координата осі X для перевірки лінійної інтерполяції поправки (мм)."
    )
    return parser


def main() -> int:
    """Точка входу виконання CLI-конвеєра."""
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[УВАГА] Вхідний файл '{input_path}' не знайдено.")
        print(f"[ІНФО] Генеруємо реалістичний тестовий набір даних інтерферометра: {input_path}")
        generate_sample_interferometer_data(input_path)

    try:
        # 1. Завантаження та перевірка формату даних інтерферометра
        samples = CompensationTable.load_interferometer_file(input_path)

        # 2. Налаштування геометричного плеча Аббе та математичного компенсатора
        arm = AbbeArm(dy=args.arm_dy, dz=args.arm_dz, dx=args.arm_dx)
        compensator = AbbeCompensator(arm=arm, default_unit=args.unit)

        # 3. Розрахунок лінійної похибки Аббе та протилежних поправок
        corrections = compensator.compute_corrections(samples)

        # 4. Формування компенсаційної таблиці та валідація сітки
        table = CompensationTable(corrections)
        grid_step = table.validate_grid(step_tolerance=args.step_tolerance)

        # 5. Експорт у структуровані формати ЧПУ
        linuxcnc_path = Path(args.out_linuxcnc)
        fanuc_path = Path(args.out_fanuc)
        csv_path = Path(args.out_csv)

        table.export_linuxcnc(linuxcnc_path)
        table.export_fanuc(fanuc_path, axis_name="X")
        table.export_csv(csv_path)

        # 6. Тестова лінійна інтерполяція в реальному часі
        interp_corr = table.interpolate(args.test_pos)

        # 7. Друк метрологічного звіту
        print_metrology_report(
            arm=arm,
            unit=args.unit,
            table=table,
            step=grid_step,
            test_pos=args.test_pos,
            interp_corr=interp_corr,
            linuxcnc_path=linuxcnc_path,
            fanuc_path=fanuc_path,
            csv_path=csv_path
        )
        return 0

    except MetrologyDataError as e:
        print(f"\n[ПОМИЛКА МЕТРОЛОГІЇ] Помилка калібрувальних даних: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[КРИТИЧНА ПОМИЛКА] Непередбачений збій виконання: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
