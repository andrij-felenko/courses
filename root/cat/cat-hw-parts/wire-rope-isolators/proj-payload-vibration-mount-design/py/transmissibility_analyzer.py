"""
Модуль розрахунку динамічної передатності T(f) та візуалізації АЧХ.
"""

import math
from typing import List, Tuple


class TransmissibilityAnalyzer:
    """
    Аналізатор амплітудно-частотної характеристики віброізоляції.
    """

    @staticmethod
    def calculate_transmissibility(f_hz: float, f0_hz: float, zeta: float) -> float:
        """
        Коефіцієнт передачі коливань (Transmissibility):
        T(r) = sqrt( (1 + (2*zeta*r)^2) / ((1 - r^2)^2 + (2*zeta*r)^2) ), де r = f / f0.
        """
        if f0_hz <= 0:
            return 1.0
        r = f_hz / f0_hz
        numerator = 1.0 + (2.0 * zeta * r) ** 2
        denominator = (1.0 - r ** 2) ** 2 + (2.0 * zeta * r) ** 2
        return math.sqrt(numerator / denominator)

    @classmethod
    def get_frequency_response(
        cls, f0_hz: float, zeta: float, f_min: float = 1.0, f_max: float = 60.0, steps: int = 120
    ) -> List[Tuple[float, float]]:
        """
        Генерує масив пар (частота, коефіцієнт передачі T).
        """
        data = []
        df = (f_max - f_min) / steps
        for i in range(steps + 1):
            f = f_min + i * df
            t_val = cls.calculate_transmissibility(f, f0_hz, zeta)
            data.append((round(f, 2), round(t_val, 3)))
        return data

    @classmethod
    def render_ascii_achx(
        cls,
        f0_hz: float,
        zeta: float,
        width: int = 55,
        height: int = 14,
    ) -> str:
        """
        Побудова текстового графіка АЧХ передатності T(f) в консолі.
        """
        data = cls.get_frequency_response(f0_hz, zeta, f_min=1.0, f_max=50.0, steps=width)
        max_t = max(t for _, t in data)
        scale_t = max(3.5, max_t * 1.1)

        grid = [[" " for _ in range(width)] for _ in range(height)]
        f_iso = f0_hz * math.sqrt(2.0)

        # Рівень T = 1.0 (межа ефективної віброізоляції)
        y_unit = int((1.0 / scale_t) * (height - 1))
        if 0 <= y_unit < height:
            for x in range(width):
                grid[height - 1 - y_unit][x] = "-"

        for x, (f, t) in enumerate(data):
            if x >= width:
                break
            y = int((t / scale_t) * (height - 1))
            if 0 <= y < height:
                grid[height - 1 - y][x] = "*"

        lines = ["    ^ Передатність T(f)"]
        for row_idx, row in enumerate(grid):
            val = scale_t * (1.0 - row_idx / (height - 1))
            lines.append(f"{val:4.1f}|" + "".join(row))
        lines.append("    +" + "-" * width + "> Частота f (Гц)")
        lines.append(f"     1.0 Гц       f0={f0_hz:.1f} Гц (Резонанс)   f_iso={f_iso:.1f} Гц")
        lines.append(f"  Легенда: * — Крива T(f);  --- Лінія нейтральної передачі T=1.0")
        return "\n".join(lines)
