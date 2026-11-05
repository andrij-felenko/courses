"""
Головний файл координації тестування міцності нарізних втулок.
"""

from insert_test_logger import InsertTestLogger
from yield_detector import YieldDetector
from plot_pullout_curve import PulloutVisualizer


def main() -> None:
    print("================================================================")
    print("  СИСТЕМА АВТОМАТИЗАЦІЇ ВИПРОБУВАНЬ НАРІЗНИХ ВТУЛОК НА ВИРИВАННЯ")
    print("================================================================")

    # 1. Збір телеметрії
    logger = InsertTestLogger()
    print("Запуск тестової сесії навантаження (симуляція UART 115200 бод)...")
    raw_data = logger.record_test(simulation=True)
    print(f"Зібрано {len(raw_data)} вимірювальних точок.")

    # 2. Обробка та детектування критичних точок
    detector = YieldDetector(smoothing_window=5)
    yield_point, peak_point = detector.analyze_pullout(raw_data)

    print("\nРезультати аналізу міцності кріплення:")
    print(f" -> Межа плинності пластику (Yield Point): {yield_point[1]:.1f} Н (при t = {yield_point[0]:.2f} с)")
    print(f" -> Пікове зусилля виривання (Peak Pullout Force): {peak_point[1]:.1f} Н (при t = {peak_point[0]:.2f} с)")

    # 3. Візуалізація кривої
    print("\nГрафік залежності сили від часу F(t):")
    chart = PulloutVisualizer.render_ascii_plot(raw_data, yield_point, peak_point)
    print(chart)

    # Спроба збереження графічного звіту
    if PulloutVisualizer.save_plot_image(raw_data, yield_point, peak_point):
        print("\nГрафік успішно експортовано у файл pullout_curve.png.")

    # 4. Оцінка відповідності стандарту
    print("\nІнженерний висновок:")
    if peak_point[1] >= 500.0:
        print(" [ВІДПОВІДАЄ СТАНДАРТУ] Нарізна втулка M3 забезпечує розрахункове утримання понад 500 Н.")
    else:
        print(" [БРАК] Зусилля утримання недостатнє. Збільшіть товщину стінки бобишки або оптимізуйте накатку.")
    print("================================================================")


if __name__ == "__main__":
    main()
