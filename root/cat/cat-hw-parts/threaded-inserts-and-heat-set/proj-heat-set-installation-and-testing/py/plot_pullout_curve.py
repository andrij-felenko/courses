"""
Модуль візуалізації кривої виривання втулки та маркування критичних точок.
"""

from typing import List, Tuple


class PulloutVisualizer:
    """
    Генератор графіків механічних випробувань.
    """

    @staticmethod
    def render_ascii_plot(
        data: List[Tuple[float, float]],
        yield_pt: Tuple[float, float],
        peak_pt: Tuple[float, float],
        width: int = 50,
        height: int = 15,
    ) -> str:
        """
        Формує наочний текстовий графік зусилля від часу для звіту в терміналі.
        """
        if not data:
            return "Немає даних для побудови графіка."

        max_t = data[-1][0] if data[-1][0] > 0 else 1.0
        max_f = peak_pt[1] * 1.15 if peak_pt[1] > 0 else 100.0

        grid = [[" " for _ in range(width)] for _ in range(height)]

        for t, f in data:
            x = int((t / max_t) * (width - 1))
            y = int((f / max_f) * (height - 1))
            if 0 <= x < width and 0 <= y < height:
                grid[height - 1 - y][x] = "."

        # Позначаємо межу плинності 'Y' та пік 'P'
        yx = int((yield_pt[0] / max_t) * (width - 1))
        yy = int((yield_pt[1] / max_f) * (height - 1))
        if 0 <= yx < width and 0 <= yy < height:
            grid[height - 1 - yy][yx] = "Y"

        px = int((peak_pt[0] / max_t) * (width - 1))
        py = int((peak_pt[1] / max_f) * (height - 1))
        if 0 <= px < width and 0 <= py < height:
            grid[height - 1 - py][px] = "P"

        lines = ["    ^ Зусилля F (Н)"]
        for row_idx, row in enumerate(grid):
            val = int(max_f * (1.0 - row_idx / (height - 1)))
            lines.append(f"{val:4d}|" + "".join(row))
        lines.append("    +" + "-" * width + "> Час t (с)")
        lines.append(f"     0.0" + " " * (width - 10) + f"{max_t:.1f} c")
        lines.append("\n  Легенда: Y — Межа плинності бобишки; P — Пікове зусилля виривання (Pullout Peak)")
        return "\n".join(lines)

    @staticmethod
    def save_plot_image(
        data: List[Tuple[float, float]],
        yield_pt: Tuple[float, float],
        peak_pt: Tuple[float, float],
        output_filename: str = "pullout_curve.png",
    ) -> bool:
        """
        Зберігає високоякісний графік F(t) у файл PNG за допомогою matplotlib.
        """
        try:
            import matplotlib.pyplot as plt

            times = [pt[0] for pt in data]
            forces = [pt[1] for pt in data]

            plt.figure(figsize=(8, 5))
            plt.plot(times, forces, label="Крива навантаження F(t)", color="#1f77b4", linewidth=2.0)
            plt.scatter([yield_pt[0]], [yield_pt[1]], color="#ff7f0e", s=100, zorder=5, label=f"Межа плинності ({yield_pt[1]:.1f} Н)")
            plt.scatter([peak_pt[0]], [peak_pt[1]], color="#d62728", s=100, zorder=5, label=f"Пік виривання ({peak_pt[1]:.1f} Н)")

            plt.title("Діаграма випробування нарізної втулки на виривання", fontsize=12)
            plt.xlabel("Час випробування t (с)", fontsize=10)
            plt.ylabel("Зусилля виривання F (Н)", fontsize=10)
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.legend(loc="upper left")
            plt.tight_layout()
            plt.savefig(output_filename, dpi=150)
            plt.close()
            return True
        except ImportError:
            return False
