"""
oscilloscope_trace.py
Завантаження, валідація та цифрова обробка оцифрованих осцилограм.

Забезпечує перевірку монотонності часової шкали, фільтрацію шумів та викидів АЦП,
розрахунок стаціонарних рівнів напруги (0% і 100%), пошук точок перетину порогових рівнів
методом лінійної інтерполяції, обчислення тривалості наростання фронту (rise time)
та постійної часу RC-перехідного процесу τ.
"""
from dataclasses import dataclass
from enum import Enum
import math
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

# Фізико-математичні константи перехідних процесів першого порядку
LN_9: float = math.log(9.0)  # ≈ 2.1972245773362196 (t_r = tau * ln(9) для рівнів 10%-90%)
LN_0_9: float = math.log(0.9)  # ≈ -0.1053605156578263 (момент перетину 10% відносно старту)
E_INV: float = math.exp(-1.0)  # ≈ 0.36787944117144233
LEVEL_63_2: float = 1.0 - E_INV  # ≈ 0.6321205588285577 (поріг 1 - 1/e для часу tau)


@dataclass(frozen=True)
class SamplePoint:
    """
    Дискретна вибірка сигналу з цифрового осцилографа.

    Атрибути:
        time_s: Часова мітка відліку в секундах.
        voltage_v: Миттєве значення напруги у вольтах.
    """
    time_s: float
    voltage_v: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.time_s):
            raise ValueError(f"Часова мітка повинна бути скінченним числом, отримано: {self.time_s}")
        if not math.isfinite(self.voltage_v):
            raise ValueError(f"Напруга повинна бути скінченним числом, отримано: {self.voltage_v}")


class EdgeSlope(str, Enum):
    """
    Напрямок перехідного процесу (нахил фронту сигналу).
    """
    RISING = "rising"    # Наростаючий фронт (перехід від базової лінії до полиці)
    FALLING = "falling"  # Спадний фронт (перехід від верхнього рівня до бази)


class OscilloscopeTrace:
    """
    Інкапсуляція оцифрованого масиву відліків осцилограми та методи цифрової обробки.

    Відповідає за валідацію часової послідовності, фільтрацію викидів дискретизації,
    статистичне визначення рівнів базової лінії та полиці імпульсу, субдискретну
    лінійну інтерполяцію моментів перетину порогів та розрахунок динамічних параметрів.
    """

    def __init__(
        self, samples: Optional[Sequence[Union[SamplePoint, Tuple[float, float]]]] = None
    ) -> None:
        self._samples: List[SamplePoint] = []
        if samples:
            for s in samples:
                if isinstance(s, SamplePoint):
                    self._samples.append(s)
                elif isinstance(s, (tuple, list)) and len(s) == 2:
                    self._samples.append(SamplePoint(float(s[0]), float(s[1])))
                else:
                    raise TypeError(f"Некоректний тип вибірки: {type(s)}. Очікувався SamplePoint або (час, напруга).")

    @classmethod
    def from_csv(
        cls,
        file_path: Union[str, Path],
        time_col: int = 0,
        voltage_col: int = 1,
        delimiter: str = ",",
        skip_header: bool = True,
    ) -> "OscilloscopeTrace":
        """
        Завантаження осцилограми з текстового CSV-файлу цифрового осцилографа.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Файл осцилограми не знайдено: {path}")

        samples: List[SamplePoint] = []
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        start_idx = 1 if skip_header and len(lines) > 0 else 0
        for line in lines[start_idx:]:
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            parts = line_str.split(delimiter)
            if len(parts) <= max(time_col, voltage_col):
                continue
            try:
                t = float(parts[time_col].strip())
                v = float(parts[voltage_col].strip())
                samples.append(SamplePoint(time_s=t, voltage_v=v))
            except ValueError:
                # Пропуск некоректних рядків або текстових заголовків
                continue

        return cls(samples)

    @property
    def samples(self) -> List[SamplePoint]:
        """Повертає список відліків осцилограми."""
        return self._samples

    def add_sample(self, time_s: float, voltage_v: float) -> None:
        """Додавання однієї точки вибірки (час у секундах, напруга у вольтах)."""
        self._samples.append(SamplePoint(float(time_s), float(voltage_v)))

    def __len__(self) -> int:
        return len(self._samples)

    def __getitem__(self, index: int) -> SamplePoint:
        return self._samples[index]

    def validate_monotonicity(self) -> bool:
        """
        Перевірка строгої хронологічної монотонності часової шкали.
        Повертає True, якщо час кожного наступного відліку суворо більший за попередній.
        """
        if len(self._samples) < 2:
            return True
        for i in range(1, len(self._samples)):
            if self._samples[i].time_s <= self._samples[i - 1].time_s:
                return False
        return True

    def filter_outliers(self, max_spike_delta_v: float = 1.5) -> None:
        """
        Фільтрація поодиноких імпульсних викидів (spikes) АЦП.
        Якщо точка різко вибивається від обох сусідів, тоді як самі сусіди
        знаходяться на близьких рівнях, значення замінюється їхнім середнім.
        """
        if len(self._samples) < 3:
            return

        cleaned = list(self._samples)
        for i in range(1, len(self._samples) - 1):
            v_prev = self._samples[i - 1].voltage_v
            v_curr = self._samples[i].voltage_v
            v_next = self._samples[i + 1].voltage_v

            delta_prev = abs(v_curr - v_prev)
            delta_next = abs(v_curr - v_next)
            neighbor_diff = abs(v_prev - v_next)

            if (
                delta_prev > max_spike_delta_v
                and delta_next > max_spike_delta_v
                and neighbor_diff <= max_spike_delta_v
            ):
                cleaned[i] = SamplePoint(self._samples[i].time_s, 0.5 * (v_prev + v_next))

        self._samples = cleaned

    def filter_moving_average(self, window_size: int = 3) -> None:
        """
        Згладжування шумів квантування та високочастотних перешкод ковзним середнім.
        """
        if len(self._samples) < window_size or window_size < 2:
            return

        half_w = window_size // 2
        smoothed: List[SamplePoint] = []
        n = len(self._samples)

        for i in range(n):
            start = max(0, i - half_w)
            end = min(n, i + half_w + 1)
            count = end - start
            avg_v = sum(self._samples[k].voltage_v for k in range(start, end)) / count
            smoothed.append(SamplePoint(self._samples[i].time_s, avg_v))

        self._samples = smoothed

    def calculate_amplitude_levels(
        self, window_fraction: float = 0.1
    ) -> Optional[Tuple[float, float]]:
        """
        Визначення стаціонарних рівнів напруги (базова лінія 0% та верхня полиця 100%).
        Усереднює пре-імпульсну та пост-імпульсну квазістаціонарні зони осцилограми.
        Повертає кортеж (baseline_v, steady_state_v) або None при замалій амплітуді.
        """
        n = len(self._samples)
        if n < 10:
            return None

        window_size = max(3, int(n * window_fraction))
        base_v = sum(self._samples[i].voltage_v for i in range(window_size)) / window_size
        top_v = sum(self._samples[n - 1 - i].voltage_v for i in range(window_size)) / window_size

        # Перевірка наявності змістовного стрибка амплітуди (щонайменше 1 мВ)
        if abs(top_v - base_v) < 1.0e-3:
            return None

        return (base_v, top_v)

    def find_threshold_crossing_time(
        self, target_voltage: float, slope: EdgeSlope = EdgeSlope.RISING
    ) -> Optional[float]:
        """
        Субдискретне визначення часової мітки перетину заданої напруги
        за допомогою лінійної інтерполяції між двома суміжними відліками.
        """
        if len(self._samples) < 2:
            return None

        for i in range(len(self._samples) - 1):
            p1 = self._samples[i]
            p2 = self._samples[i + 1]
            v1, v2 = p1.voltage_v, p2.voltage_v
            t1, t2 = p1.time_s, p2.time_s

            if slope == EdgeSlope.RISING:
                if v1 <= target_voltage <= v2 and v2 > v1:
                    fraction = (target_voltage - v1) / (v2 - v1)
                    return t1 + fraction * (t2 - t1)
            else:
                if v1 >= target_voltage >= v2 and v1 > v2:
                    fraction = (v1 - target_voltage) / (v1 - v2)
                    return t1 + fraction * (t2 - t1)

        return None

    def find_fraction_crossing_time(
        self, fraction: float, slope: EdgeSlope = EdgeSlope.RISING
    ) -> Optional[float]:
        """
        Пошук моменту перетину відносного рівня амплітуди (наприклад, 0.10, 0.632, 0.90).
        """
        levels = self.calculate_amplitude_levels()
        if levels is None:
            return None
        base_v, top_v = levels
        target_v = base_v + fraction * (top_v - base_v)
        return self.find_threshold_crossing_time(target_v, slope)

    def calculate_rise_time(
        self, lower_percent: float = 0.10, upper_percent: float = 0.90
    ) -> Optional[float]:
        """
        Розрахунок тривалості наростання фронту (rise time) між пороговими рівнями
        (за замовчуванням 10% та 90% від повної амплітуди сигналу).
        """
        if not (0.0 <= lower_percent < upper_percent <= 1.0):
            return None

        levels = self.calculate_amplitude_levels()
        if levels is None:
            return None
        base_v, top_v = levels
        if top_v <= base_v:
            return None

        amplitude = top_v - base_v
        v_low = base_v + lower_percent * amplitude
        v_high = base_v + upper_percent * amplitude

        t_low = self.find_threshold_crossing_time(v_low, EdgeSlope.RISING)
        t_high = self.find_threshold_crossing_time(v_high, EdgeSlope.RISING)

        if t_low is not None and t_high is not None and t_high > t_low:
            return t_high - t_low

        return None

    def calculate_tau(self, method: str = "rise_time") -> Optional[float]:
        """
        Розрахунок постійної часу RC-ланцюга τ = R * C.

        Параметри:
            method: Спосіб обчислення:
                - "rise_time": на основі 10%-90% наростання: τ = t_r / ln(9) ≈ t_r / 2.1972
                - "threshold_63": на основі інтерполяції точки 63.2% (1 - 1/e):
                  τ = (t_63.2% - t_10%) / (1 + ln(0.9))
        """
        if method == "rise_time":
            tr = self.calculate_rise_time(0.10, 0.90)
            if tr is not None and tr > 0.0:
                return tr / LN_9
            return None

        if method == "threshold_63":
            t_10 = self.find_fraction_crossing_time(0.10, EdgeSlope.RISING)
            t_63 = self.find_fraction_crossing_time(LEVEL_63_2, EdgeSlope.RISING)
            if t_10 is not None and t_63 is not None and t_63 > t_10:
                # Оскільки t_10 = t_start - tau*ln(0.9), а t_63 = t_start + tau,
                # маємо: t_63 - t_10 = tau * (1 + ln(0.9)) ≈ 0.89464 * tau
                scale = 1.0 + LN_0_9
                if scale > 0.0:
                    return (t_63 - t_10) / scale
            return None

        raise ValueError(f"Невідомий метод розрахунку tau: {method}. Допустимі: 'rise_time', 'threshold_63'.")
