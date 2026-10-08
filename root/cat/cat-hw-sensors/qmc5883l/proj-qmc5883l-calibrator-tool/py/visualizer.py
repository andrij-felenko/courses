"""
visualizer.py
Модуль візуалізації реального часу на базі Matplotlib для побудови 3D-хмари
сирих та відкаліброваних вимірювань, контролю повноти сферичного покриття
при обертанні компаса та графічного відображення апроксимованого еліпсоїда.
"""
import logging
from typing import Optional, Tuple

import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class CalibrationVisualizer:
    """
    Клас для відображення 3D-точок вимірювань компаса QMC5883L,
    порівняння сирого еліпсоїда з відкаліброваною сферою та побудови графічних звітів.
    """

    def __init__(self, interactive: bool = True) -> None:
        self.interactive = interactive
        if not self.interactive:
            matplotlib.use("Agg")

        self.fig: Optional[plt.Figure] = None
        self.ax_raw: Optional[Axes3D] = None
        self.ax_calib: Optional[Axes3D] = None

    def setup_figure(self) -> Tuple[plt.Figure, Axes3D, Axes3D]:
        """Створює двохпанельне вікно 3D-візуалізації."""
        self.fig = plt.figure(figsize=(14, 6))
        self.fig.suptitle("Автокалібрування цифрового компаса QMC5883L (Hard/Soft-Iron)", fontsize=14, fontweight="bold")

        self.ax_raw = self.fig.add_subplot(1, 2, 1, projection="3d")
        self.ax_raw.set_title("Сирі вимірювання (Спотворений еліпсоїд)")
        self.ax_raw.set_xlabel("X (LSB)")
        self.ax_raw.set_ylabel("Y (LSB)")
        self.ax_raw.set_zlabel("Z (LSB)")

        self.ax_calib = self.fig.add_subplot(1, 2, 2, projection="3d")
        self.ax_calib.set_title("Відкалібровані вимірювання (Сфера)")
        self.ax_calib.set_xlabel("X_cal")
        self.ax_calib.set_ylabel("Y_cal")
        self.ax_calib.set_zlabel("Z_cal")

        if self.interactive:
            plt.ion()
            plt.show(block=False)

        return self.fig, self.ax_raw, self.ax_calib

    def plot_comparison(
        self,
        raw_points: np.ndarray,
        calibrated_points: Optional[np.ndarray] = None,
        hard_iron_offset: Optional[np.ndarray] = None,
        output_filepath: Optional[str] = None,
    ) -> None:
        """
        Будує 3D-графіки сирих даних та відкаліброваної сфери.
        При наявності hard_iron_offset відображає зміщений центр еліпсоїда.
        """
        if self.fig is None or self.ax_raw is None or self.ax_calib is None:
            self.setup_figure()

        assert self.ax_raw is not None
        assert self.ax_calib is not None

        self.ax_raw.cla()
        self.ax_calib.cla()

        self.ax_raw.set_title("Сирі вимірювання (Спотворений еліпсоїд)")
        self.ax_raw.set_xlabel("X")
        self.ax_raw.set_ylabel("Y")
        self.ax_raw.set_zlabel("Z")

        self.ax_calib.set_title("Відкалібровані вимірювання (Сфера)")
        self.ax_calib.set_xlabel("X_cal")
        self.ax_calib.set_ylabel("Y_cal")
        self.ax_calib.set_zlabel("Z_cal")

        if len(raw_points) > 0:
            self.ax_raw.scatter(
                raw_points[:, 0],
                raw_points[:, 1],
                raw_points[:, 2],
                c="tab:red",
                marker="o",
                s=10,
                alpha=0.6,
                label="Сирі точки QMC5883L",
            )

        if hard_iron_offset is not None:
            self.ax_raw.scatter(
                [hard_iron_offset[0]],
                [hard_iron_offset[1]],
                [hard_iron_offset[2]],
                c="black",
                marker="X",
                s=100,
                label="Центр (Hard-Iron Offset)",
            )
        self.ax_raw.legend(loc="upper right")

        if calibrated_points is not None and len(calibrated_points) > 0:
            self.ax_calib.scatter(
                calibrated_points[:, 0],
                calibrated_points[:, 1],
                calibrated_points[:, 2],
                c="tab:green",
                marker="o",
                s=10,
                alpha=0.6,
                label="Відкалібровані точки",
            )

            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            xs = np.outer(np.cos(u), np.sin(v))
            ys = np.outer(np.sin(u), np.sin(v))
            zs = np.outer(np.ones(np.size(u)), np.cos(v))

            target_r = float(np.mean(np.linalg.norm(calibrated_points, axis=1)))
            self.ax_calib.plot_wireframe(
                xs * target_r,
                ys * target_r,
                zs * target_r,
                color="tab:blue",
                alpha=0.25,
                linewidth=0.8,
            )
            self.ax_calib.legend(loc="upper right")

        if self.fig is not None:
            self.fig.canvas.draw()
            if self.interactive:
                plt.pause(0.01)

        if output_filepath and self.fig is not None:
            self.fig.savefig(output_filepath, dpi=300, bbox_inches="tight")
            logging.info(f"3D-графік калібрування збережено у файл: {output_filepath}")

    def close(self) -> None:
        """Закриває графічні вікна."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
