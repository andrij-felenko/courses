# vent_flow_calc.py

"""
Модуль для розрахунку параметрів вентиляції та вирівнювання тиску 
в герметичних корпусах за допомогою захисних ePTFE мембран.
Враховує закон Шарля, рівняння стану ідеального газу та характеристики повітропроникності.
"""

import math


class EnclosureVentCalculator:
    """
    Клас для моделювання термодинамічних процесів у герметичному корпусі
    під час температурних коливань та розрахунку параметрів ePTFE мембрани.
    """

    def __init__(self, volume_liters: float, initial_temp_c: float = 20.0):
        """
        Ініціалізація параметрів корпусу.

        :param volume_liters: Об'єм герметичної частини корпусу в літрах (л)
        :param initial_temp_c: Початкова температура всередині корпусу в градусах Цельсія (°C)
        """
        if volume_liters <= 0:
            raise ValueError("Об'єм корпусу має бути більше нуля.")
        
        self.volume_m3 = volume_liters * 1e-3  # Переведення літрів у кубічні метри (м³)
        self.initial_temp_k = initial_temp_c + 273.15  # Переведення в Кельвіни

    def calculate_max_flow_rate(self, final_temp_c: float, duration_minutes: float) -> dict:
        """
        Обчислює максимальну (пікову) об'ємну витрату повітря, що витікає або засмоктується,
        на основі рівняння стану ідеального газу (закон Менделєєва-Клапейрона / закон Шарля).

        Формула: Q = (V / T) * (dT / dt)
        
        :param final_temp_c: кінцева температура всередині корпусу (°C)
        :param duration_minutes: Час зміни температури (хвилин)
        :return: Словник з результатами розрахунку (об'ємна витрата в л/хв, м³/год, тощо)
        """
        if duration_minutes <= 0:
            raise ValueError("Час зміни температури має бути більше нуля.")

        final_temp_k = final_temp_c + 273.15
        dt_seconds = duration_minutes * 60.0

        # Швидкість зміни температури (K/с)
        temp_rate_k_per_s = (final_temp_k - self.initial_temp_k) / dt_seconds

        # Об'ємна витрата повітря при нормальних умовах (або міттєва при середній температурі)
        # Q (м³/с) = V (м³) / T (K) * (dT/dt) (K/с)
        # Використовуємо середню температуру процесу для більшої точності
        avg_temp_k = (self.initial_temp_k + final_temp_k) / 2.0
        
        flow_rate_m3_s = (self.volume_m3 / avg_temp_k) * abs(final_temp_k - self.initial_temp_k) / dt_seconds
        
        # Переведення в більш зручні одиниці
        flow_rate_l_min = flow_rate_m3_s * 60.0 * 1000.0
        flow_rate_l_hour = flow_rate_l_min * 60.0

        # Розрахунок витісненого об'єму повітря (у літрах при нормальних умовах)
        delta_v_liters = self.volume_m3 * abs(final_temp_k - self.initial_temp_k) / self.initial_temp_k * 1000.0

        return {
            "delta_v_liters": delta_v_liters,
            "flow_rate_l_min": flow_rate_l_min,
            "flow_rate_l_hour": flow_rate_l_hour,
            "flow_rate_m3_s": flow_rate_m3_s,
            "temp_rate_k_min": (final_temp_c - (self.initial_temp_k - 273.15)) / duration_minutes
        }

    def select_membrane_area(self, peak_flow_l_min: float, specific_airflow_rate: float, 
                             target_pressure_drop_mbar: float = 70.0) -> float:
        """
        Визначає мінімально необхідну ефективну площу ePTFE мембрани.

        :param peak_flow_l_min: Пікова об'ємна витрата повітря (л/хв)
        :param specific_airflow_rate: Питома повітропроникність мембрани (наприклад, мл/хв/см² при 70 мбар)
        :param target_pressure_drop_mbar: Допустимий перепад тиску на мембрані (мбар), зазвичай 70 мбар
        :return: Мінімальна площа мембрани в квадратних сантиметрах (см²)
        """
        if specific_airflow_rate <= 0:
            raise ValueError("Питома витрата мембрани має бути більше нуля.")

        # Припускаємо лінійну залежність витрати від перепаду тиску для малих значень або використовуємо паспортну величину
        # Площа (см²) = Пікова витрата (мл/хв) / Питома витрата (мл/хв/см²)
        peak_flow_ml_min = peak_flow_l_min * 1000.0
        min_area_cm2 = peak_flow_ml_min / specific_airflow_rate

        return min_area_cm2


if __name__ == "__main__":
    print("--- Демонстрація розрахунку вентиляції герметичного корпусу ---")
    
    # Вихідні дані згідно з вимогами:
    # Об'єм корпусу = 2.5 л
    # Зміна температури: від 55 °C до 15 °C (охолодження, засмоктування повітря всередину)
    # Час = 10 хвилин
    volume = 2.5  # л
    t_start = 55.0  # °C
    t_end = 15.0  # °C
    duration = 10.0  # хв

    calculator = EnclosureVentCalculator(volume_liters=volume, initial_temp_c=t_start)
    results = calculator.calculate_max_flow_rate(final_temp_c=t_end, duration_minutes=duration)

    print(f"Об'єм корпусу: {volume} л")
    print(f"Зміна температури: {t_start} °C -> {t_end} °C за {duration} хв")
    print(f"Об'єм повітря, що витісняється/засмоктується: {results['delta_v_liters']:.3f} л")
    print(f"Максимальна об'ємна витрата повітря: {results['flow_rate_l_min']:.3f} л/хв ({results['flow_rate_l_hour']:.2f} л/год)")

    # Приклад підбору ePTFE мембрани
    # Типова питома повітропроникність захисної мембрани (наприклад, µVent) ~ 400 мл/хв/см² при перепаді 70 мбар
    specific_flow = 400.0  # мл/хв/см²
    min_area = calculator.select_membrane_area(results['flow_rate_l_min'], specific_flow)

    print(f"\nПараметри ePTFE мембрани:")
    print(f"Питома повітропроникність: {specific_flow} мл/хв/см² (при 70 мбар)")
    print(f"Мінімально необхідна ефективна площа мембрани: {min_area:.2f} см²")
