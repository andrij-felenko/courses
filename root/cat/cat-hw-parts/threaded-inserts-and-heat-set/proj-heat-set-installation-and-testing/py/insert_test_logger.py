"""
Модуль реєстрації телеметрії випробування нарізних втулок через UART або емулятор.
"""

import csv
from typing import Generator, List, Tuple


class InsertTestLogger:
    """
    Клас збору даних випробування на виривання нарізних втулок.
    """

    def __init__(self, port: str = "COM3", baudrate: int = 115200) -> None:
        self.port = port
        self.baudrate = baudrate
        self.records: List[Tuple[float, float]] = []

    def simulate_telemetry_stream(
        self,
        peak_force_n: float = 650.0,
        yield_force_n: float = 480.0,
        total_time_s: float = 5.0,
        steps: int = 250,
    ) -> Generator[Tuple[float, float], None, None]:
        """
        Генерує реалістичну криву виривання втулки:
        1) Пружна зона: лінійне зростання до yield_force_n
        2) Пластична зона зминання бобишки: сповільнення росту до peak_force_n
        3) Зрив втулки: різкий спад зусилля
        """
        dt = total_time_s / steps
        for i in range(steps):
            t = i * dt
            if t < 2.0:
                # Зона пружності матеріалу (пружна деформація полімеру)
                force = (t / 2.0) * yield_force_n
            elif t < 3.2:
                # Зона пластичної плинності до пікового опору
                progress = (t - 2.0) / 1.2
                force = yield_force_n + (peak_force_n - yield_force_n) * (1.0 - (1.0 - progress) ** 2)
            elif t < 3.8:
                # Зрив шліців втулки зі стінок отвору
                progress = (t - 3.2) / 0.6
                force = peak_force_n * (1.0 - progress * 0.85)
            else:
                # Залишкове тертя ковзання вирваної втулки
                force = peak_force_n * 0.15

            # Додаємо невеликий вимірювальний шум тензомосту
            noise = (i % 5 - 2) * 1.5
            yield (round(t, 3), max(0.0, round(force + noise, 2)))

    def record_test(self, simulation: bool = True) -> List[Tuple[float, float]]:
        """
        Виконує тестовий прогін та фіксує масив точок (час, сила).
        """
        self.records.clear()
        if simulation:
            for timestamp, force in self.simulate_telemetry_stream():
                self.records.append((timestamp, force))
        return self.records

    def export_csv(self, filename: str) -> None:
        """
        Зберігає результати випробувань у файл CSV.
        """
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Час_с", "Зусилля_Н"])
            for t, f_val in self.records:
                writer.writerow([t, f_val])
