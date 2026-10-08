"""
telemetry_plotter.py
Візуалізація телеметричних даних INA219 та результатів аналізу живлення за допомогою pandas та matplotlib.
Побудова багатопанельних графіків кривих розряду акумулятора, часових профілів напруги, струму й потужності.
"""
import logging
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Безпечний рендеринг у файл без відкриття GUI-вікон
import matplotlib.pyplot as plt
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class TelemetryPlotter:
    """
    Застосування pandas та matplotlib для побудови багатопанельних графіків
    розрядних кривих акумулятора, профілів споживання потужності та часових
    залежностей напруги й струму.
    """

    def __init__(self, style: str = "seaborn-v0_8-whitegrid") -> None:
        try:
            plt.style.use(style)
        except Exception:
            plt.style.use("default")

    def plot_summary(
        self,
        df: pd.DataFrame,
        cutoff_voltage: float = 9.0,
        output_path: Optional[str] = None,
        title: str = "Аналіз телеметрії живлення INA219 та розряду акумулятора",
    ) -> plt.Figure:
        """
        Будує 4-панельний графічний звіт:
        1. Крива розряду напруги від часу V_bus(t).
        2. Залежність напруги від вирядженої ємності V_bus(mAh).
        3. Профілі струму I(t) та потужності P(t) від часу.
        4. Динаміка рівня заряду SoC(t) (%) та розподіл навантаження.
        """
        time_rel = df["timestamp"] - df["timestamp"].iloc[0]

        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(title, fontsize=14, fontweight="bold")

        # Панель 1: Напруга шини від часу V_bus(t)
        axs[0, 0].plot(time_rel, df["v_bus"], color="tab:blue", linewidth=2, label="V_bus (В)")
        axs[0, 0].axhline(y=cutoff_voltage, color="tab:red", linestyle="--", label=f"Cut-off ({cutoff_voltage} В)")
        axs[0, 0].set_title("Графік розряду напруги шини від часу", fontsize=11)
        axs[0, 0].set_xlabel("Час (с)", fontsize=10)
        axs[0, 0].set_ylabel("Напруга шини (В)", fontsize=10)
        axs[0, 0].legend(loc="upper right")
        axs[0, 0].grid(True, linestyle=":", alpha=0.6)

        # Панель 2: Разрядна крива напруги від спожитої ємності V_bus(mAh)
        capacity = df["cum_capacity_mah"] if "cum_capacity_mah" in df.columns else time_rel
        axs[0, 1].plot(capacity, df["v_bus"], color="tab:purple", linewidth=2, label="V_bus (В)")
        axs[0, 1].axhline(y=cutoff_voltage, color="tab:red", linestyle="--", label=f"Cut-off ({cutoff_voltage} В)")
        axs[0, 1].set_title("Разрядна крива: Напруга vs Спожита ємність", fontsize=11)
        axs[0, 1].set_xlabel("Спожита ємність (мА·год)", fontsize=10)
        axs[0, 1].set_ylabel("Напруга шини (В)", fontsize=10)
        axs[0, 1].legend(loc="upper right")
        axs[0, 1].grid(True, linestyle=":", alpha=0.6)

        # Панель 3: Профілі струму I(t) та потужності P(t)
        ax3_1 = axs[1, 0]
        ax3_2 = ax3_1.twinx()
        l1 = ax3_1.plot(time_rel, df["current_ma"], color="tab:green", linewidth=1.5, label="Струм (мА)")
        l2 = ax3_2.plot(time_rel, df["power_mw"], color="tab:orange", linewidth=1.5, linestyle="-.", label="Потужність (мВт)")
        ax3_1.set_title("Профілі струму та споживання потужності", fontsize=11)
        ax3_1.set_xlabel("Час (с)", fontsize=10)
        ax3_1.set_ylabel("Струм (мА)", color="tab:green", fontsize=10)
        ax3_2.set_ylabel("Потужність (мВт)", color="tab:orange", fontsize=10)
        lines = l1 + l2
        labels = [l.get_label() for l in lines]
        ax3_1.legend(lines, labels, loc="upper right")
        ax3_1.grid(True, linestyle=":", alpha=0.6)

        # Панель 4: Динаміка рівня заряду SoC (%)
        if "soc_pct" in df.columns:
            axs[1, 1].plot(time_rel, df["soc_pct"], color="tab:red", linewidth=2, label="SoC (%)")
            axs[1, 1].set_ylabel("Рівень заряду SoC (%)", fontsize=10)
        else:
            axs[1, 1].hist(df["current_ma"], bins=20, color="tab:cyan", edgecolor="black", alpha=0.7)
            axs[1, 1].set_ylabel("Частота", fontsize=10)

        axs[1, 1].set_title("Динаміка рівня заряду акумулятора (SoC)", fontsize=11)
        axs[1, 1].set_xlabel("Час (с)", fontsize=10)
        axs[1, 1].set_ylim(-5, 105)
        axs[1, 1].grid(True, linestyle=":", alpha=0.6)

        plt.tight_layout()

        if output_path:
            self.save_plot(fig, output_path)

        return fig

    def save_plot(self, fig: plt.Figure, output_path: str) -> None:
        """Зберігає графік у файл (PNG або PDF)."""
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logging.info(f"Графічний звіт успішно збережено у файл: {output_path}")
        plt.close(fig)
