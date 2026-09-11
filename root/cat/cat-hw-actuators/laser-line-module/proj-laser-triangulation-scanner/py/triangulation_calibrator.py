"""Модуль тріангуляційного калібрування та перерахунку піксельних зсувів у фізичну висоту (мм).

Перетворює субпіксельні відхилення лінії від базової площини у фізичний метричний
профіль рельєфу за допомогою поліноміальної моделі тріангуляції.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np


class TriangulationHeightMapper:
    """Зберігання калібрувальних коефіцієнтів тріангуляції та перетворення піксельних

    відхилень профілю у фізичну висоту поверхні.
    """

    def __init__(
        self,
        pixel_size_x_mm: float = 0.05,
        default_scale_z_mm_per_px: float = 0.04,
    ) -> None:
        """Ініціалізує калібратор геометричними параметрами.

        Параметри:
            pixel_size_x_mm: Масштабний коефіцієнт по горизонталі (мм/піксель у площині лінії).
            default_scale_z_mm_per_px: Лінійне наближення чутливості по Z (мм/піксель зміщення).
        """
        self.pixel_size_x_mm = float(pixel_size_x_mm)
        self.default_scale_z = float(default_scale_z_mm_per_px)

        # Коефіцієнти базової лінії площини: v_base(u) = b0 + b1*u (за замовчуванням v = 260.0)
        self.baseline_poly: np.ndarray = np.array([260.0], dtype=np.float64)

        # Коефіцієнти перетворення зсуву delta_v у висоту Z (мм):
        # Поліном першого порядку: Z(delta_v) = a * delta_v + b
        self.height_poly: np.ndarray = np.array([self.default_scale_z, 0.0], dtype=np.float64)

        self.u_center_px: float = 320.0
        self.is_calibrated: bool = False

    def calibrate_baseline(
        self,
        u_coords: np.ndarray,
        v_coords: np.ndarray,
        poly_order: int = 1,
    ) -> None:
        """Виконує калібрування нульової базової площини (столу) за еталонним знімком.

        Параметри:
            u_coords: Горизонтальні координати стовпців.
            v_coords: Виміряні вертикальні координати лазерної смуги на площині.
            poly_order: Порядок полінома (1 — пряма лінія, 2 — параболічна дуга).
        """
        valid = ~np.isnan(v_coords)
        if np.count_nonzero(valid) < 10:
            raise ValueError("Недостатньо валідних точок для калібрування базової площини.")

        u_valid = u_coords[valid].astype(np.float64)
        v_valid = v_coords[valid].astype(np.float64)

        # Апроксимація форми базової лінії поліномом: np.polyfit повертає коефіцієнти від вищого до 0
        self.baseline_poly = np.polyfit(u_valid, v_valid, deg=poly_order)
        self.u_center_px = float(np.mean(u_valid))
        self.is_calibrated = True

    def fit_height_polynomial(
        self,
        measured_shifts_px: np.ndarray,
        known_heights_mm: np.ndarray,
        poly_order: int = 2,
    ) -> None:
        """Калібрує нелінійну залежність висоти Z (мм) від піксельного зсуву delta_v.

        Використовує набір калібрувальних мір висоти (кінцевих мір довжини або сходинок).
        """
        shifts = np.asarray(measured_shifts_px, dtype=np.float64)
        heights = np.asarray(known_heights_mm, dtype=np.float64)

        if len(shifts) != len(heights) or len(shifts) < 2:
            raise ValueError("Потрібно щонайменше 2 точки калібрування зсув-висота.")

        # Фіксуємо нульовий зсув на нульовій висоті: додаємо (0, 0)
        if not np.any(np.isclose(shifts, 0.0)):
            shifts = np.append(shifts, 0.0)
            heights = np.append(heights, 0.0)

        # Підгонка полінома: Z(delta_v)
        self.height_poly = np.polyfit(shifts, heights, deg=poly_order)

    def compute_baseline_profile(self, u_coords: np.ndarray) -> np.ndarray:
        """Обчислює вертикальні координати базової площини для заданих стовпців."""
        return np.polyval(self.baseline_poly, u_coords.astype(np.float64)).astype(np.float32)

    def pixel_to_metric(
        self,
        u_coords: np.ndarray,
        v_subpixel: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Перетворює координати детектора у фізичні просторові величини (X, Z).

        Параметри:
            u_coords: Масив горизонтальних піксельних координат.
            v_subpixel: Масив виміряних субпіксельних положень лінії.

        Повертає:
            x_mm: Фізична координата вздовж довжини лазерної смуги (мм).
            z_mm: Фізична висота рельєфу відносно базової площини (мм).
            delta_v_px: Піксельний оптичний зсув лінії.
        """
        v_base = self.compute_baseline_profile(u_coords)

        # Оптичний зсув: за стандартною тріангуляційною геометрією виступ над площиною
        # зміщує лінію в бік менших індексів рядка (v_base - v_subpixel)
        delta_v_px = v_base - v_subpixel

        # Фізична горизонтальна координата (центрована відносно оптичної осі)
        x_mm = (u_coords.astype(np.float32) - float(self.u_center_px)) * self.pixel_size_x_mm

        # Фізична висота Z (мм) за поліноміальною калібрувальною моделлю
        valid = ~np.isnan(delta_v_px)
        z_mm = np.full_like(delta_v_px, np.nan, dtype=np.float32)

        if np.any(valid):
            valid_shifts = delta_v_px[valid].astype(np.float64)
            z_mm[valid] = np.polyval(self.height_poly, valid_shifts).astype(np.float32)

        return x_mm, z_mm, delta_v_px

    def save_calibration(self, filepath: str | Path) -> None:
        """Зберігає параметри калібрування у JSON-файл."""
        data = {
            "pixel_size_x_mm": self.pixel_size_x_mm,
            "default_scale_z": self.default_scale_z,
            "baseline_poly": self.baseline_poly.tolist(),
            "height_poly": self.height_poly.tolist(),
            "u_center_px": self.u_center_px,
            "is_calibrated": self.is_calibrated,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_calibration(self, filepath: str | Path) -> None:
        """Завантажує параметри калібрування з JSON-файлу."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.pixel_size_x_mm = float(data["pixel_size_x_mm"])
        self.default_scale_z = float(data["default_scale_z"])
        self.baseline_poly = np.array(data["baseline_poly"], dtype=np.float64)
        self.height_poly = np.array(data["height_poly"], dtype=np.float64)
        self.u_center_px = float(data["u_center_px"])
        self.is_calibrated = bool(data["is_calibrated"])
