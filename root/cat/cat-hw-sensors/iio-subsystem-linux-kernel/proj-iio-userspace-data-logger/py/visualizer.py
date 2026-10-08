"""Модуль динамічної візуалізації даних IIO IMU в реальному часі на базі Matplotlib."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from typing import Dict, Callable, Any, Optional


class RealtimeVisualizer:
    """Візуалізація потокових даних акселерометра та гіроскопа в реальному часі.

    Створює вікна і графіки Matplotlib для відображення динаміки осей X, Y, Z
    акселерометра та гіроскопа в реальному часі з ковзним вікном спостереження.
    """

    def __init__(self, history_size: int = 200, update_interval_ms: int = 50) -> None:
        """Ініціалізація візуалізатора Matplotlib.

        :param history_size: Кількість точок на графіку часових серій (ковзне вікно).
        :param update_interval_ms: Інтервал оновлення кадру графіків у мілісекундах.
        """
        self.history_size = history_size
        self.update_interval_ms = update_interval_ms
        self.anim: Optional[animation.FuncAnimation] = None

        plt.style.use("seaborn-v0_8-darkgrid" if "seaborn-v0_8-darkgrid" in plt.style.available else "default")
        self.fig, (self.ax_accel, self.ax_gyro) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
        self.fig.canvas.manager.set_window_title("IIO Linux IMU — Потоковий моніторинг реального часу")

        self.x_data = np.arange(self.history_size)

        (self.line_ax,) = self.ax_accel.plot(self.x_data, np.zeros(self.history_size), 'r-', label='Accel X (м/с²)', lw=1.5)
        (self.line_ay,) = self.ax_accel.plot(self.x_data, np.zeros(self.history_size), 'g-', label='Accel Y (м/с²)', lw=1.5)
        (self.line_az,) = self.ax_accel.plot(self.x_data, np.zeros(self.history_size), 'b-', label='Accel Z (м/с²)', lw=1.5)

        self.ax_accel.set_title("Динаміка акселерометра (м/с²)", fontsize=12, fontweight='bold')
        self.ax_accel.set_ylabel("Прискорення [м/с²]", fontsize=10)
        self.ax_accel.legend(loc="upper right", frameon=True)
        self.ax_accel.grid(True, linestyle='--', alpha=0.7)
        self.ax_accel.set_ylim(-20, 20)

        (self.line_gx,) = self.ax_gyro.plot(self.x_data, np.zeros(self.history_size), 'r--', label='Gyro X (рад/с)', lw=1.5)
        (self.line_gy,) = self.ax_gyro.plot(self.x_data, np.zeros(self.history_size), 'g--', label='Gyro Y (рад/с)', lw=1.5)
        (self.line_gz,) = self.ax_gyro.plot(self.x_data, np.zeros(self.history_size), 'b--', label='Gyro Z (рад/с)', lw=1.5)

        self.ax_gyro.set_title("Динаміка гіроскопа (рад/с)", fontsize=12, fontweight='bold')
        self.ax_gyro.set_xlabel("Відліки часу (ковзне вікно)", fontsize=10)
        self.ax_gyro.set_ylabel("Кутова швидкість [рад/с]", fontsize=10)
        self.ax_gyro.legend(loc="upper right", frameon=True)
        self.ax_gyro.grid(True, linestyle='--', alpha=0.7)
        self.ax_gyro.set_ylim(-5, 5)

        self.fig.tight_layout()

    def update_plots(self, history_data: Dict[str, np.ndarray]) -> None:
        """Оновлює дані ліній графіків на основі нових масивів історії.

        :param history_data: Словник з масивами вимірів для кожної осі IMU.
        """
        accel_x = history_data.get("accel_x", np.zeros(0))
        accel_y = history_data.get("accel_y", np.zeros(0))
        accel_z = history_data.get("accel_z", np.zeros(0))
        gyro_x = history_data.get("gyro_x", np.zeros(0))
        gyro_y = history_data.get("gyro_y", np.zeros(0))
        gyro_z = history_data.get("gyro_z", np.zeros(0))

        n_pts = len(accel_x)
        if n_pts > 0:
            x_vals = np.arange(n_pts)

            self.line_ax.set_data(x_vals, accel_x)
            self.line_ay.set_data(x_vals, accel_y)
            self.line_az.set_data(x_vals, accel_z)

            self.line_gx.set_data(x_vals, gyro_x)
            self.line_gy.set_data(x_vals, gyro_y)
            self.line_gz.set_data(x_vals, gyro_z)

            self.ax_accel.set_xlim(0, max(n_pts, self.history_size))
            self.ax_gyro.set_xlim(0, max(n_pts, self.history_size))

            for ax in (self.ax_accel, self.ax_gyro):
                ax.relim()
                ax.autoscale_view(scalex=False, scaley=True)

    def start_animation(self, update_callback: Callable[[], Dict[str, np.ndarray]]) -> None:
        """Запускає цикл анімації Matplotlib.

        :param update_callback: Функція зчитування нових даних, яка повертає словник історії.
        """
        def _anim_wrapper(frame_idx: int):
            history_data = update_callback()
            self.update_plots(history_data)
            return (
                self.line_ax, self.line_ay, self.line_az,
                self.line_gx, self.line_gy, self.line_gz
            )

        self.anim = animation.FuncAnimation(
            self.fig,
            _anim_wrapper,
            interval=self.update_interval_ms,
            blit=False,
            cache_frame_data=False
        )
        plt.show()
