"""
main.py
Головний виконуваний скрипт для моніторингу живлення та аналізу телеметрії INA219.
Створює тестовий телеметричний потік, запускає прийомопередач через TelemetryReceiver,
виконує аналіз у BatteryPowerAnalyzer та будує графіки у TelemetryPlotter.
"""
import logging
import math
import os
import time
from typing import Dict, List

from power_analyzer import BatteryPowerAnalyzer
from telemetry_plotter import TelemetryPlotter
from telemetry_receiver import TelemetryReceiver, TelemetryDataError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def generate_simulated_ina219_stream(
    duration_sec: float = 60.0,
    sample_interval: float = 0.5,
    v_start: float = 12.4,
    v_cutoff: float = 9.2,
    base_current_ma: float = 450.0,
) -> List[Dict[str, float]]:
    """
    Генерує реалістичний симульований часовий ряд вимірювань INA219 для розряду акумулятора
    із пульсаціями струму, падінням напруги під навантаженням та поодинокими аномальними викидами.
    """
    data = []
    num_samples = int(duration_sec / sample_interval)
    start_ts = time.time()

    for i in range(num_samples):
        t_rel = i * sample_interval
        ts = start_ts + t_rel

        decay = (t_rel / duration_sec) ** 1.2
        v_bus = v_start - decay * (v_start - v_cutoff)

        pulse = 250.0 if (i % 20 < 5) else 0.0
        current_ma = base_current_ma + pulse + 15.0 * math.sin(i * 0.5)

        v_shunt_mv = current_ma * 0.1
        power_mw = v_bus * current_ma

        # Додавання аномальних викидів кожні 50 вибірок для перевірки фільтрації
        if i > 0 and i % 50 == 0:
            v_bus = 99.0  # Аномальна напруга
        elif i > 0 and i % 75 == 0:
            current_ma = -9999.0  # Аномальний струм

        data.append(
            {
                "timestamp": round(ts, 3),
                "v_bus": round(v_bus, 3),
                "v_shunt_mv": round(v_shunt_mv, 3),
                "current_ma": round(current_ma, 2),
                "power_mw": round(power_mw, 2),
            }
        )

    return data


def main() -> None:
    """Головний конвеєр обробки телеметрії INA219."""
    logging.info("=== Запуск системи моніторингу та аналізу живлення INA219 ===")

    csv_file = "ina219_telemetry.csv"
    plot_png_file = "battery_discharge_report.png"
    plot_pdf_file = "battery_discharge_report.pdf"

    nominal_capacity = 2200.0  # мА·год
    full_voltage = 12.6        # В
    cutoff_voltage = 9.0       # В

    # 1. Ініціалізація та запуск збору телеметрії через TelemetryReceiver
    receiver = TelemetryReceiver(
        connection_type="mock",
        voltage_min=5.0,
        voltage_max=15.0,
        current_max=3000.0,
        power_max=45000.0,
    )
    receiver.connect()

    logging.info("Генерація тестового телеметричного потоку розряду батареї...")
    raw_stream = generate_simulated_ina219_stream(
        duration_sec=120.0,
        sample_interval=0.5,
        v_start=12.4,
        v_cutoff=9.2,
        base_current_ma=500.0,
    )

    valid_samples = receiver.start_collection(
        duration_seconds=120.0,
        output_file=csv_file,
        file_format="csv",
        simulated_data=raw_stream,
    )
    receiver.disconnect()

    logging.info(f"Отримано та відфільтровано {len(valid_samples)} валідних записів телеметрії.")

    # 2. Обробка та аналіз за допомогою BatteryPowerAnalyzer
    analyzer = BatteryPowerAnalyzer(
        nominal_capacity_mah=nominal_capacity,
        full_voltage=full_voltage,
        cutoff_voltage=cutoff_voltage,
    )

    df_telemetry = analyzer.load_data_from_file(csv_file)
    df_processed = analyzer.calculate_capacity_and_energy(df_telemetry)
    df_final = analyzer.calculate_soc(df_processed)

    report = analyzer.generate_energy_report(df_final)

    # 3. Візуалізація та генерація графічних звітів через TelemetryPlotter
    plotter = TelemetryPlotter()
    plotter.plot_summary(
        df_final,
        cutoff_voltage=cutoff_voltage,
        output_path=plot_png_file,
        title="Звіт розряду акумулятора та моніторингу INA219",
    )
    plotter.plot_summary(
        df_final,
        cutoff_voltage=cutoff_voltage,
        output_path=plot_pdf_file,
        title="Звіт розряду акумулятора та моніторингу INA219 (PDF)",
    )

    logging.info("=== Обробку телеметрії та генерацію звітів успішно завершено ===")


if __name__ == "__main__":
    main()
