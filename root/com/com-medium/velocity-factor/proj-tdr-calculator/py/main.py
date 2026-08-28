from dataclasses import dataclass
from typing import Optional
import math

C_VACUUM_MM_PS: float = 0.299792458  # швидкість світла у мм/пс


@dataclass(frozen=True)
class TdrMeasurement:
    distance_mm: float
    propagation_delay_ps_mm: float


@dataclass(frozen=True)
class TraceSkew:
    time_skew_ps: float
    meander_length_mm: float


def calculate_tdr(velocity_factor: float, delta_t_ps: float) -> Optional[TdrMeasurement]:
    """Обчислює відстань до місця обриву кабелю методом TDR."""
    if not (0.0 < velocity_factor <= 1.0) or delta_t_ps < 0:
        return None

    v_signal = C_VACUUM_MM_PS * velocity_factor
    distance = (v_signal * delta_t_ps) / 2.0
    t_pd = 1.0 / v_signal

    return TdrMeasurement(distance_mm=distance, propagation_delay_ps_mm=t_pd)


def calculate_skew(len1_mm: float, len2_mm: float, velocity_factor: float) -> Optional[TraceSkew]:
    """Обчислює розсинхронізм між двома трасами та довжину компенсаційного меандру."""
    if not (0.0 < velocity_factor <= 1.0) or len1_mm < 0 or len2_mm < 0:
        return None

    v_signal = C_VACUUM_MM_PS * velocity_factor
    t_pd = 1.0 / v_signal
    diff_len = abs(len1_mm - len2_mm)
    skew = diff_len * t_pd

    return TraceSkew(time_skew_ps=skew, meander_length_mm=diff_len)


if __name__ == "__main__":
    # Тест TDR для кабелю з VF = 0.66
    tdr_res = calculate_tdr(velocity_factor=0.66, delta_t_ps=101010.0)
    if tdr_res:
        print(f"--- TDR Рефлектометрія (Python) ---")
        print(f"Відстань до пошкодження: {tdr_res.distance_mm / 1000.0:.3f} м")
        print(f"Погонна затримка:        {tdr_res.propagation_delay_ps_mm:.3f} пс/мм")

    # Тест вирівнювання трас на FR-4 (VF = 0.55)
    skew_res = calculate_skew(len1_mm=120.0, len2_mm=135.0, velocity_factor=0.55)
    if skew_res:
        print(f"\n--- Вирівнювання трас PCB ---")
        print(f"Часовий зсув:            {skew_res.time_skew_ps:.2f} пс")
        print(f"Компенсаційний меандр:   {skew_res.meander_length_mm:.2f} мм")
