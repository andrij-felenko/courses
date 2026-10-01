"""Модуль аналізу та оцінки поверхневого опору ізоляції (SIR)."""

import math
from dataclasses import dataclass, field


@dataclass
class SIRAnalysisResult:
    """Збереження часового ряду вимірювань, мінімального значення опору та статусу проходження випробування."""
    timestamps_sec: list[float] = field(default_factory=list)
    resistances_ohms: list[float] = field(default_factory=list)
    min_resistance_ohms: float = 0.0
    passed_ipc_criteria: bool = False
    failure_reason: str = ""


class IPCSIRChecker:
    """Обчислення динаміки опору SIR, виявлення дендритного падіння опору та верифікація порогової умови IPC."""

    # Стандарт IPC-TM-650 метод 2.6.3.7 вимагає опір > 100 МОм (1e8 Ом)
    IPC_THRESHOLD_OHMS: float = 1.0e8

    def __init__(self, threshold_ohms: float = IPC_THRESHOLD_OHMS):
        self.threshold_ohms = threshold_ohms

    def calculate_sir(self, voltage_v: float, current_a: float) -> float:
        """
        Обчислює поверхневий опір ізоляції R = V / I.
        Обробляє випадок нульового або надто малого струму для запобігання діленню на нуль.
        """
        if current_a <= 1.0e-15:
            return 1.0e14  # Максимально можливий опір для межі електрометра (100 ТОм)
        return voltage_v / current_a

    def apply_logarithmic_smoothing(self, resistances: list[float], window_size: int = 3) -> list[float]:
        """Застосовує логарифмічне рухоме усереднення для фільтрації високочастотного вимірювального шуму."""
        if len(resistances) < window_size:
            return list(resistances)

        smoothed = []
        for i in range(len(resistances)):
            start_idx = max(0, i - window_size + 1)
            chunk = resistances[start_idx : i + 1]
            log_sum = sum(math.log10(val) for val in chunk)
            avg_log = log_sum / len(chunk)
            smoothed.append(10.0 ** avg_log)

        return smoothed

    def evaluate(self, timestamps: list[float], raw_voltages: list[float], raw_currents: list[float]) -> SIRAnalysisResult:
        """Проводить повний аналіз часового ряду та верифікацію за стандартом IPC-TM-650."""
        result = SIRAnalysisResult()
        result.timestamps_sec = list(timestamps)

        raw_resistances = [
            self.calculate_sir(v, i) for v, i in zip(raw_voltages, raw_currents)
        ]
        result.resistances_ohms = self.apply_logarithmic_smoothing(raw_resistances)

        if not result.resistances_ohms:
            result.passed_ipc_criteria = False
            result.failure_reason = "Відсутні дані вимірювань"
            return result

        result.min_resistance_ohms = min(result.resistances_ohms)

        # Перевірка дендритного падіння опору (різке падіння понад 1 порядок)
        dendrite_detected = False
        for k in range(1, len(result.resistances_ohms)):
            prev_r = result.resistances_ohms[k - 1]
            curr_r = result.resistances_ohms[k]
            if prev_r > 0 and (curr_r / prev_r) < 0.1:
                dendrite_detected = True
                break

        if result.min_resistance_ohms < self.threshold_ohms:
            result.passed_ipc_criteria = False
            result.failure_reason = f"Мінімальний опір ({result.min_resistance_ohms:.2e} Ом) нижче IPC порогу ({self.threshold_ohms:.2e} Ом)"
        elif dendrite_detected:
            result.passed_ipc_criteria = False
            result.failure_reason = "Виявлено дендритний пробій (аномальне падіння опору)"
        else:
            result.passed_ipc_criteria = True
            result.failure_reason = "Залишки флюсу FVS-7 відповідають нормам IPC-TM-650"

        return result
