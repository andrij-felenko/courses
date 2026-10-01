"""Головний модуль автоматизованого випробування залишків флюсу FVS-7."""

import time
from sir_meter import ElectrometerClient
from ipc_evaluator import IPCSIRChecker


def main() -> None:
    print("=== Автоматизоване випробування SIR для залишків флюсу FVS-7 ===")

    client = ElectrometerClient(port="COM3", baudrate=9600)
    client.connect()

    checker = IPCSIRChecker()

    timestamps = []
    voltages = []
    currents = []

    # Імітація 10 послідовних відліків тестового циклу
    total_samples = 10
    sample_interval_sec = 0.2

    for n in range(total_samples):
        v, i = client.read_measurement()
        current_time = n * sample_interval_sec

        timestamps.append(current_time)
        voltages.append(v)
        currents.append(i)

        sir_value = checker.calculate_sir(v, i)
        print(f"[{current_time:.1f} с] Напруга: {v:.1f} В | Струм витоку: {i:.2e} А | SIR: {sir_value:.2e} Ом")
        time.sleep(0.05)

    client.disconnect()

    # Аналіз та формування підсумкового вердикту
    analysis = checker.evaluate(timestamps, voltages, currents)

    print("\n--- Результати аналізу за стандартом IPC-TM-650 ---")
    print(f"Мінімальний розрахований опір: {analysis.min_resistance_ohms:.2e} Ом")
    print(f"Статус відповідності: {'ПРОЙДЕНО (PASSED)' if analysis.passed_ipc_criteria else 'НЕ ПРОЙДЕНО (FAILED)'}")
    print(f"Деталі: {analysis.failure_reason}")


if __name__ == "__main__":
    main()
