"""
Модуль цифрової фільтрації сигналу та детектування точок руйнування різьбової посадки.
"""

from typing import List, Tuple


class YieldDetector:
    """
    Аналізатор динаміки навантаження та пошуку межі плинності бобишки.
    """

    def __init__(self, smoothing_window: int = 5) -> None:
        self.smoothing_window = smoothing_window

    def smooth_signal(self, data: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Згладжування ковзним середнім для фільтрації шумів тензодатчика.
        """
        if len(data) < self.smoothing_window:
            return data

        smoothed: List[Tuple[float, float]] = []
        half = self.smoothing_window // 2

        for i in range(len(data)):
            start = max(0, i - half)
            end = min(len(data), i + half + 1)
            window_forces = [pt[1] for pt in data[start:end]]
            avg_force = sum(window_forces) / len(window_forces)
            smoothed.append((data[i][0], round(avg_force, 2)))

        return smoothed

    def analyze_pullout(
        self, data: List[Tuple[float, float]]
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Визначає:
        1) Точку межі плинності (Yield Point) за спадом похідної dF/dt на 40% від початкової пружної жорсткості.
        2) Точку максимального опору вириванню (Peak Pullout Force).
        """
        smoothed = self.smooth_signal(data)
        if not smoothed:
            return ((0.0, 0.0), (0.0, 0.0))

        # 1. Пошук абсолютного піку сили
        peak_idx = 0
        max_f = -1.0
        for i, (t, f) in enumerate(smoothed):
            if f > max_f:
                max_f = f
                peak_idx = i

        peak_point = smoothed[peak_idx]

        # 2. Обчислення початкової пружної жорсткості k_initial = dF/dt у першій третині до піку
        early_limit = max(2, peak_idx // 3)
        initial_derivatives = []
        for i in range(1, early_limit):
            dt = smoothed[i][0] - smoothed[i - 1][0]
            if dt > 0:
                initial_derivatives.append((smoothed[i][1] - smoothed[i - 1][1]) / dt)

        base_stiffness = sum(initial_derivatives) / len(initial_derivatives) if initial_derivatives else 100.0

        # 3. Пошук межі плинності (де похідна падає нижче 60% від початкової пружної жорсткості)
        yield_idx = early_limit
        for i in range(early_limit, peak_idx):
            dt = smoothed[i][0] - smoothed[i - 1][0]
            if dt > 0:
                current_d = (smoothed[i][1] - smoothed[i - 1][1]) / dt
                if current_d < 0.60 * base_stiffness:
                    yield_idx = i
                    break

        yield_point = smoothed[yield_idx]
        return (yield_point, peak_point)
