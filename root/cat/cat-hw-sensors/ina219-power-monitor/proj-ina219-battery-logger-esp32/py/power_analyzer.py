"""
power_analyzer.py
Обробка та аналіз телеметрії живлення INA219, чисельне інтегрування,
обчислення ємності (мА·год), спожитої енергії (Вт·год), рівня заряду (SoC)
та оцінка внутрішнього опору акумулятора.
"""
import json
import logging
from typing import Any, Dict

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class BatteryPowerAnalyzer:
    """
    Обробка збережених часових рядів, чисельне інтегрування миттєвого струму й потужності
    за часовими мітками (мА·год, Вт·год), розрахунок глибини розряду (SoC) та аналіз
    ефективної ємності акумулятора.
    """

    def __init__(
        self,
        nominal_capacity_mah: float = 2500.0,
        full_voltage: float = 12.6,
        cutoff_voltage: float = 9.0,
    ) -> None:
        self.nominal_capacity_mah = nominal_capacity_mah
        self.full_voltage = full_voltage
        self.cutoff_voltage = cutoff_voltage

    def load_data_from_file(self, filepath: str) -> pd.DataFrame:
        """Завантажує часовий ряд телеметрії з файлу CSV або JSON у pandas DataFrame."""
        if filepath.endswith(".json"):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            df = pd.read_csv(filepath)

        return self.prepare_dataframe(df)

    def prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Перевіряє та впорядковує стовпчики DataFrame за часом."""
        required_cols = ["timestamp", "v_bus", "current_ma", "power_mw"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Відсутня необхідна колонка '{col}' у даних телеметрії")

        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    def calculate_capacity_and_energy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Обчислює накопичену ємність (мА·год) та спожиту енергію (Вт·год)
        шляхом чисельного інтегрування миттєвого струму й потужності методом трапецій.
        Додає нові колонки cum_capacity_mah, cum_energy_wh та dt_sec до DataFrame.
        """
        df = df.copy()
        timestamps = df["timestamp"].values
        currents_ma = df["current_ma"].values
        powers_mw = df["power_mw"].values

        n = len(df)
        dt_sec = np.zeros(n)
        cum_capacity_mah = np.zeros(n)
        cum_energy_wh = np.zeros(n)

        if n > 1:
            dt_sec[1:] = np.diff(timestamps)
            # Обчислення приросту за методом трапецій для кожного інтервалу:
            # dQ = (I_{i-1} + I_i) / 2 * dt / 3600  (мА·год)
            # dE = (P_{i-1} + P_i) / 2 * dt / 3600 / 1000 (Вт·год)
            delta_q = 0.5 * (currents_ma[:-1] + currents_ma[1:]) * (dt_sec[1:] / 3600.0)
            delta_e = 0.5 * (powers_mw[:-1] + powers_mw[1:]) * (dt_sec[1:] / 3600.0 / 1000.0)

            cum_capacity_mah[1:] = np.cumsum(delta_q)
            cum_energy_wh[1:] = np.cumsum(delta_e)

        df["dt_sec"] = dt_sec
        df["cum_capacity_mah"] = cum_capacity_mah
        df["cum_energy_wh"] = cum_energy_wh

        return df

    def calculate_soc(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Розраховує рівень заряду акумулятора (State of Charge, SoC у %)
        на основі кулонівського підрахунку накопиченої ємності та напруги.
        """
        df = df.copy()
        if "cum_capacity_mah" not in df.columns:
            df = self.calculate_capacity_and_energy(df)

        # Кулонівський SoC (%) = 100 * (1 - Q_consumed / Q_nominal)
        soc_coulomb = 100.0 * (1.0 - (df["cum_capacity_mah"] / self.nominal_capacity_mah))
        soc_coulomb = np.clip(soc_coulomb, 0.0, 100.0)

        # Напруговий оціночний SoC (%)
        v_span = self.full_voltage - self.cutoff_voltage
        if v_span > 0:
            soc_voltage = 100.0 * (df["v_bus"] - self.cutoff_voltage) / v_span
            soc_voltage = np.clip(soc_voltage, 0.0, 100.0)
        else:
            soc_voltage = soc_coulomb

        df["soc_coulomb_pct"] = soc_coulomb
        df["soc_voltage_pct"] = soc_voltage
        df["soc_pct"] = soc_coulomb  # Основний показник

        return df

    def estimate_internal_resistance(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Оцінює внутрішній опір акумулятора під навантаженням.
        Використовує відношення перепаду напруги до зміни струму між сусідніми кроками.
        R_int = dV / dI (Ом).
        """
        if len(df) < 2:
            return {"avg_r_internal_ohm": 0.0, "max_r_internal_ohm": 0.0}

        dv = np.abs(np.diff(df["v_bus"].values))  # В
        di_a = np.abs(np.diff(df["current_ma"].values)) / 1000.0  # А

        # Фільтруємо зміни струму, суттєво більші за шум (> 50 мА)
        valid_mask = di_a > 0.05
        if not np.any(valid_mask):
            return {"avg_r_internal_ohm": 0.0, "max_r_internal_ohm": 0.0}

        r_int_samples = dv[valid_mask] / di_a[valid_mask]
        # Відсіюємо нереалістичні сплески (> 5 Ом)
        r_int_samples = r_int_samples[r_int_samples < 5.0]

        if len(r_int_samples) == 0:
            return {"avg_r_internal_ohm": 0.0, "max_r_internal_ohm": 0.0}

        return {
            "avg_r_internal_ohm": float(np.mean(r_int_samples)),
            "max_r_internal_ohm": float(np.max(r_int_samples)),
            "min_r_internal_ohm": float(np.min(r_int_samples)),
        }

    def generate_energy_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Формує підсумковий звіт енергетичного балансу пристрою та акумулятора.
        """
        df_processed = self.calculate_soc(df)
        r_int_data = self.estimate_internal_resistance(df_processed)

        total_time_sec = float(df_processed["timestamp"].iloc[-1] - df_processed["timestamp"].iloc[0])
        total_capacity_mah = float(df_processed["cum_capacity_mah"].iloc[-1])
        total_energy_wh = float(df_processed["cum_energy_wh"].iloc[-1])

        initial_voltage = float(df_processed["v_bus"].iloc[0])
        final_voltage = float(df_processed["v_bus"].iloc[-1])
        avg_current_ma = float(df_processed["current_ma"].mean())
        max_current_ma = float(df_processed["current_ma"].max())
        avg_power_mw = float(df_processed["power_mw"].mean())
        max_power_mw = float(df_processed["power_mw"].max())

        effective_efficiency_pct = min(100.0, (total_capacity_mah / self.nominal_capacity_mah) * 100.0)

        report = {
            "duration_sec": round(total_time_sec, 2),
            "duration_hours": round(total_time_sec / 3600.0, 4),
            "total_capacity_mah": round(total_capacity_mah, 2),
            "total_energy_wh": round(total_energy_wh, 4),
            "initial_voltage_v": round(initial_voltage, 3),
            "final_voltage_v": round(final_voltage, 3),
            "voltage_drop_v": round(initial_voltage - final_voltage, 3),
            "avg_current_ma": round(avg_current_ma, 2),
            "max_current_ma": round(max_current_ma, 2),
            "avg_power_mw": round(avg_power_mw, 2),
            "max_power_mw": round(max_power_mw, 2),
            "final_soc_pct": round(float(df_processed["soc_pct"].iloc[-1]), 2),
            "effective_efficiency_pct": round(effective_efficiency_pct, 2),
            "internal_resistance": r_int_data,
        }

        logging.info("--- Підсумковий звіт енергетичного балансу ---")
        logging.info(f"Тривалість спостереження: {report['duration_sec']} с ({report['duration_hours']} год)")
        logging.info(f"Спожита ємність: {report['total_capacity_mah']} мА·год")
        logging.info(f"Спожита енергія: {report['total_energy_wh']} Вт·год")
        logging.info(f"Сер. струм: {report['avg_current_ma']} мА, Сер. потужність: {report['avg_power_mw']} мВт")
        logging.info(f"Середній внутрішній опір: {r_int_data.get('avg_r_internal_ohm', 0):.4f} Ом")

        return report
