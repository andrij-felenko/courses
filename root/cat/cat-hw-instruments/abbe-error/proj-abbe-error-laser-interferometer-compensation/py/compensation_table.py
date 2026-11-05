"""
compensation_table.py
Реалізація класу CompensationTable для обробки та валідації калібрувальних профілів.

Здійснює розбір вхідних текстових файлів вимірювань інтерферометра, контроль
монотонності координат і стабільності кроку сітки, інтерполяцію поправок
у реальному часі та експорт у файли компенсації ЧПУ (LinuxCNC, Fanuc) і CSV.
"""
from bisect import bisect_right
import csv
import math
from pathlib import Path
import re
from typing import List, Sequence, Tuple, Union

from abbe_compensator import AbbeCorrection, InterferometerSample


class MetrologyDataError(Exception):
    """
    Спеціалізований виняток для метрологічних помилок:
    невалідний формат вхідних даних, порушення монотонності калібрувальних точок,
    нестабільність кроку сітки або неприпустимі числові значення.
    """
    pass


class CompensationTable:
    """
    Інкапсуляція калібрувальної сітки компенсації похибки Аббе вздовж осі верстата.

    Забезпечує:
        - Зчитування сирих замірів лазерного інтерферометра з файлів різних форматів;
        - Валідацію строгої монотонності та рівномірності дискретного кроку сітки;
        - Швидку лінійну інтерполяцію коригувальної поправки за O(log N) у реальному часі;
        - Генерацію стандартизованих компенсаційних файлів для ЧПУ (LinuxCNC, Fanuc) та CSV.
    """

    def __init__(self, points: Sequence[AbbeCorrection]) -> None:
        """
        Ініціалізація компенсаційної таблиці масивом точок розрахунку.

        Аргументи:
            points: Послідовність об'єктів AbbeCorrection.

        Викликає:
            MetrologyDataError: Якщо передано порожній масив точок.
        """
        if not points:
            raise MetrologyDataError("Таблиця компенсації не може бути створена з порожнього набору точок.")

        self._points: List[AbbeCorrection] = list(points)
        self._positions: List[float] = [p.position for p in self._points]
        self._corrections: List[float] = [p.correction for p in self._points]
        self._errors: List[float] = [p.abbe_error for p in self._points]

    @property
    def points(self) -> List[AbbeCorrection]:
        """Копія списку точок калібрування."""
        return list(self._points)

    @property
    def positions(self) -> List[float]:
        """Список координат положення вздовж осі X (мм)."""
        return list(self._positions)

    @property
    def corrections(self) -> List[float]:
        """Список коригувальних поправок (мм)."""
        return list(self._corrections)

    @property
    def count(self) -> int:
        """Кількість вузлів калібрувальної сітки."""
        return len(self._points)

    @property
    def travel_range(self) -> Tuple[float, float]:
        """Діапазон переміщення осі (start_mm, end_mm)."""
        return self._positions[0], self._positions[-1]

    @property
    def min_error_um(self) -> float:
        """Мінімальне зміщення Аббе в мікронах (мкм)."""
        return min(self._errors) * 1000.0

    @property
    def max_error_um(self) -> float:
        """Максимальне зміщення Аббе в мікронах (мкм)."""
        return max(self._errors) * 1000.0

    @property
    def peak_to_peak_um(self) -> float:
        """Повний розмах похибки Аббе (Peak-to-Peak / PV) у мікронах (мкм)."""
        return (max(self._errors) - min(self._errors)) * 1000.0

    @property
    def rms_error_um(self) -> float:
        """Середньоквадратичне значення похибки Аббе (RMS) у мікронах (мкм)."""
        mean_sq = sum((e * 1000.0) ** 2 for e in self._errors) / len(self._errors)
        return math.sqrt(mean_sq)

    @classmethod
    def load_interferometer_file(
        cls,
        filepath: Union[str, Path]
    ) -> List[InterferometerSample]:
        """
        Зчитування та первинна валідація файлу замірів інтерферометра.

        Підтримує текстові файли, розділені комами, крапками з комою, табуляцією або пропусками:
            <position_mm> <pitch_val> <yaw_val>
        Автоматично пропускає порожні рядки, рядки коментарів (#, ;, //) та рядок заголовка.

        Аргументи:
            filepath: Шлях до вхідного файлу вимірювань.

        Повертає:
            Список зчитаних об'єктів InterferometerSample.

        Викликає:
            MetrologyDataError: У разі відсутності файлу, пошкоджених рядків або нечислових даних.
        """
        path = Path(filepath)
        if not path.is_file():
            raise MetrologyDataError(f"Файл метрологічних вимірів не знайдено: '{path}'")

        try:
            with path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            raise MetrologyDataError(f"Помилка відкриття файлу '{path}': {e}") from e

        if not lines:
            raise MetrologyDataError(f"Файл '{path}' є повністю порожнім.")

        samples: List[InterferometerSample] = []
        for line_num, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            # Пропуск порожніх рядків та рядків коментарів
            if not line or line.startswith(("#", ";", "//")):
                continue

            # Розділення за комами, крапками з комою, табуляцією або послідовностями пробілів
            tokens = [t.strip() for t in re.split(r"[,;\t\s]+", line) if t.strip()]

            # Пропуск можливого рядка заголовка таблиці
            if any(tok.lower() in {"position", "pos", "x", "pitch", "yaw", "arcsec", "urad"} for tok in tokens):
                continue

            if len(tokens) < 3:
                raise MetrologyDataError(
                    f"Рядок {line_num}: недостатньо колонок (знайдено {len(tokens)}, потрібно 3: "
                    f"позиція, тангаж, рискання). Текст рядка: '{line}'"
                )

            try:
                pos_val = float(tokens[0])
                pitch_val = float(tokens[1])
                yaw_val = float(tokens[2])
            except ValueError as e:
                raise MetrologyDataError(
                    f"Рядок {line_num}: неможливо перетворити значення на число: '{line}'. Деталі: {e}"
                ) from e

            if not (math.isfinite(pos_val) and math.isfinite(pitch_val) and math.isfinite(yaw_val)):
                raise MetrologyDataError(
                    f"Рядок {line_num}: виявлено некоректне числове значення (NaN або Inf): '{line}'"
                )

            samples.append(InterferometerSample(position=pos_val, pitch=pitch_val, yaw=yaw_val))

        if len(samples) < 2:
            raise MetrologyDataError(
                f"Файл '{path}' містить лише {len(samples)} точок вимірювань. Для сітки потрібно щонайменше 2 точки."
            )

        return samples

    def validate_grid(self, step_tolerance: float = 1e-4) -> float:
        """
        Валідація калібрувальної сітки вздовж осі:
        - перевірка строгої монотонності зростання координат;
        - перевірка стабільності кроку між сусідніми вузлами сітки в межах допуску.

        Аргументи:
            step_tolerance: Максимально допустиме відхилення кроку від номінального (мм).

        Повертає:
            Номінальний крок калібрувальної сітки (мм).

        Викликає:
            MetrologyDataError: При порушенні монотонності або нерівномірності сітки.
        """
        if len(self._positions) < 2:
            raise MetrologyDataError("Калібрувальна сітка повинна містити щонайменше 2 точки.")

        nominal_step = self._positions[1] - self._positions[0]
        if nominal_step <= 0.0:
            raise MetrologyDataError(
                f"Порушення монотонності координат: перша точка x[0]={self._positions[0]:.4f} "
                f"та друга x[1]={self._positions[1]:.4f} дають непозитивний крок {nominal_step:.4f} мм."
            )

        for i in range(len(self._positions) - 1):
            curr_pos = self._positions[i]
            next_pos = self._positions[i + 1]
            current_step = next_pos - curr_pos

            # Перевірка строгої монотонності
            if current_step <= 0.0:
                raise MetrologyDataError(
                    f"Порушення строгої монотонності координат: точка [{i}] x={curr_pos:.4f} "
                    f">= точка [{i + 1}] x={next_pos:.4f}."
                )

            # Перевірка стабільності кроку
            step_deviation = abs(current_step - nominal_step)
            if step_deviation > step_tolerance:
                raise MetrologyDataError(
                    f"Виявлено нестабільність кроку калібрувальної сітки: між x={curr_pos:.4f} "
                    f"та x={next_pos:.4f} крок становить {current_step:.5f} мм, "
                    f"що відхиляється від базового {nominal_step:.5f} мм більше ніж на допуск {step_tolerance:.5f} мм."
                )

        return nominal_step

    def interpolate(self, target_position: float) -> float:
        """
        Обчислення проміжної поправки методом лінійної інтерполяції
        для корекції позиціонування робочого органа в реальному часі.

        Використовує бінарний пошук сусідніх вузлів для досягнення складності O(log N).
        У разі виходу за калібрований інтервал виконує насичення (clamp)
        до значення найближчої граничної точки.

        Аргументи:
            target_position: Запитана координата осі (мм).

        Повертає:
            Інтерпольоване значення компенсуючої поправки (мм).
        """
        # Граничні умови: насичення (clamp) на межах каліброваного діапазону
        if target_position <= self._positions[0]:
            return self._corrections[0]
        if target_position >= self._positions[-1]:
            return self._corrections[-1]

        # Бінарний пошук сусіднього інтервалу сітки
        idx = bisect_right(self._positions, target_position)
        x0 = self._positions[idx - 1]
        x1 = self._positions[idx]
        c0 = self._corrections[idx - 1]
        c1 = self._corrections[idx]

        # Лінійна інтерполяція між двома сусідніми вузлами
        t = (target_position - x0) / (x1 - x0)
        return c0 + t * (c1 - c0)

    def export_linuxcnc(self, filepath: Union[str, Path]) -> None:
        """
        Експорт таблиці у формат крокової компенсації гвинта LinuxCNC (COMP_FILE).

        Формат LinuxCNC:
            <номінальна_позиція> <поправка_прямого_ходу> <поправка_зворотного_ходу>
        Значення записуються в одиницях осі верстата (мм).

        Аргументи:
            filepath: Шлях до вихідного файлу (наприклад, 'abbe_linuxcnc.comp').
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            f.write("# LinuxCNC Abbe Error Screw/Guide Compensation Table\n")
            f.write(f"# Travel: {self.travel_range[0]:.3f} .. {self.travel_range[1]:.3f} mm\n")
            f.write(f"# Grid points: {self.count}\n")
            f.write("# Format: <Nominal Pos (mm)> <Forward Corr (mm)> <Reverse Corr (mm)>\n")
            for p in self._points:
                f.write(f"{p.position:12.5f} {p.correction:12.6f} {p.correction:12.6f}\n")

    def export_fanuc(
        self,
        filepath: Union[str, Path],
        axis_name: str = "X",
        multiplier_um: float = 1000.0
    ) -> None:
        """
        Експорт структурованої таблиці крокової компенсації (Pitch Error Compensation) Fanuc.

        У ЧПУ Fanuc поправки записуються в імпульсах/мікронах детектора для регулярної сітки кроку.

        Аргументи:
            filepath: Шлях до вихідного файлу (наприклад, 'abbe_fanuc.dat').
            axis_name: Позначення осі верстата (X, Y, Z).
            multiplier_um: Масштабний множник переведення мм у мікрони (за замовчуванням 1000.0).
        """
        step = self.validate_grid()
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            f.write("%\n")
            f.write("(FANUC PITCH ERROR COMPENSATION - ABBE CORRECTION)\n")
            f.write(f"(AXIS: {axis_name.upper()})\n")
            f.write(f"(START_POSITION: {self.travel_range[0]:.4f} MM)\n")
            f.write(f"(INTERVAL_STEP: {step:.4f} MM)\n")
            f.write(f"(TOTAL_POINTS: {self.count})\n")
            f.write("(UNITS: MICRONS [UM], POSITIVE=FORWARD OFFSET)\n")
            for idx, p in enumerate(self._points):
                corr_um_int = int(round(p.correction * multiplier_um))
                f.write(f"N{idx:04d} P{corr_um_int:+d}\n")
            f.write("%\n")

    def export_csv(self, filepath: Union[str, Path]) -> None:
        """
        Експорт повного метрологічного звіту калібрувальної сітки у формат CSV.

        Аргументи:
            filepath: Шлях до вихідного CSV-файлу.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "position_mm",
                "pitch_rad",
                "yaw_rad",
                "abbe_error_um",
                "correction_um",
                "correction_mm"
            ])
            for p in self._points:
                writer.writerow([
                    f"{p.position:.4f}",
                    f"{p.pitch_rad:.9e}",
                    f"{p.yaw_rad:.9e}",
                    f"{p.abbe_error * 1000.0:.4f}",
                    f"{p.correction * 1000.0:.4f}",
                    f"{p.correction:.6f}"
                ])
