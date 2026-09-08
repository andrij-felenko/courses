import math
from typing import Dict, List, Tuple

class GoelOkumotoModel:
    def __init__(self, total_defects: float, detection_rate: float):
        # total_defects (a) - оцінка початкового пулу прихованих дефектів
        # detection_rate (b) - коефіцієнт інтенсивності виявлення за одиницю часу
        if total_defects <= 0 or detection_rate <= 0:
            raise ValueError("Параметри моделі a та b повинні бути строго додатними")
        self.a = float(total_defects)
        self.b = float(detection_rate)

    def mean_failures(self, t: float) -> float:
        # Функція середнього накопичення відмов: m(t) = a * (1 - exp(-b * t))
        if t <= 0:
            return 0.0
        return self.a * (1.0 - math.exp(-self.b * t))

    def failure_intensity(self, t: float) -> float:
        # Функція миттєвої інтенсивності відмов: lambda(t) = a * b * exp(-b * t)
        if t <= 0:
            return self.a * self.b
        return self.a * self.b * math.exp(-self.b * t)

    def mtbf(self, t: float) -> float:
        # Середній наробіток до відмови: MTBF(t) = 1 / lambda(t)
        intensity = self.failure_intensity(t)
        if intensity <= 0:
            return float("inf")
        return 1.0 / intensity

    def residual_defects(self, t: float) -> float:
        # Кількість залишкових дефектів у коді: N_residual(t) = a - m(t)
        return self.a - self.mean_failures(t)

    def generate_timeline(self, max_time: float, steps: int = 10) -> List[Dict[str, float]]:
        # Генерація таблиці динаміки надійності
        timeline = []
        step_size = max_time / steps
        for i in range(steps + 1):
            t = i * step_size
            timeline.append({
                "time_hours": round(t, 2),
                "cumulative_failures": round(self.mean_failures(t), 2),
                "residual_defects": round(self.residual_defects(t), 2),
                "failure_intensity": round(self.failure_intensity(t), 4),
                "mtbf_hours": round(self.mtbf(t), 2)
            })
        return timeline
