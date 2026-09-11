"""Модуль субпіксельної локалізації лазерної лінії методом центру мас (Center of Gravity, COG).

Забезпечує високу швидкість обчислень (векторизація NumPy) та захист від шумів
камери й вторинних відблисків завдяки адаптивному порогуванню й локальному вікну.
"""

from __future__ import annotations

import numpy as np


class SubpixelCogDetector:
    """Субпіксельний детектор енергетичного центру лазерної смуги.

    Обчислює координату центру смуги вздовж кожного стовпця зображення за формулою
    зваженого центру мас яскравості (Center of Gravity, COG).
    """

    def __init__(
        self,
        threshold: float = 25.0,
        window_radius: int = 8,
        min_peak_value: float = 40.0,
        min_intensity_sum: float = 100.0,
    ) -> None:
        """Ініціалізує параметри детектора.

        Параметри:
            threshold: Постійний поріг відсікання темного фонового шуму.
            window_radius: Напівширина вікна (у пікселях) навколо піка для COG.
            min_peak_value: Мінімальна пікова яскравість стовпця для валідації лінії.
            min_intensity_sum: Мінімальна сумарна зважена яскравість у вікні.
        """
        self.threshold = float(threshold)
        self.window_radius = int(window_radius)
        self.min_peak_value = float(min_peak_value)
        self.min_intensity_sum = float(min_intensity_sum)

    def detect_subpixel_line(
        self,
        diff_image: np.ndarray,
        roi: tuple[int, int, int, int] | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Знаходить субпіксельні координати лазерної лінії по стовпцях.

        Параметри:
            diff_image: Одноканальне напівтонове зображення (градації сірого).
            roi: Кортеж (y_min, y_max, x_min, x_max) для обмеження зони пошуку.

        Повертає:
            u_coords: Масив горизонтальних координат пікселів (вісь X, цілі числа).
            v_subpixel: Масив вертикальних субпіксельних координат (вісь Y, дійсні числа).
                        Якщо у стовпці лінія відсутня або заслабка, містить np.nan.
        """
        if diff_image.ndim != 2:
            raise ValueError("Вхідне зображення повинно бути одноканальним (градації сірого).")

        img = diff_image.astype(np.float32)
        height, width = img.shape

        if roi is not None:
            y_min, y_max, x_min, x_max = roi
            y_min = max(0, int(y_min))
            y_max = min(height, int(y_max))
            x_min = max(0, int(x_min))
            x_max = min(width, int(x_max))
        else:
            y_min, y_max, x_min, x_max = 0, height, 0, width

        roi_img = img[y_min:y_max, x_min:x_max]
        roi_h, roi_w = roi_img.shape

        if roi_h == 0 or roi_w == 0:
            return np.arange(width, dtype=np.int32), np.full(width, np.nan, dtype=np.float32)

        # 1. Пошук пікової яскравості та її вертикального індексу в кожному стовпці ROI
        peak_y_idx = np.argmax(roi_img, axis=0)  # форма (roi_w,)
        peak_vals = np.max(roi_img, axis=0)      # форма (roi_w,)

        # Маска стовпців, де пік лазера перевищує мінімальний поріг
        valid_mask = peak_vals >= self.min_peak_value

        v_subpixel_roi = np.full(roi_w, np.nan, dtype=np.float32)

        # 2. Координатна сітка вертикальних індексів для векторизованого розрахунку
        y_indices = np.arange(roi_h, dtype=np.float32)[:, np.newaxis]

        # 3. Формування локального вікна навколо піка: |y - peak_y| <= window_radius
        lower_bound = np.maximum(0, peak_y_idx - self.window_radius)
        upper_bound = np.minimum(roi_h - 1, peak_y_idx + self.window_radius)

        in_window = (y_indices >= lower_bound) & (y_indices <= upper_bound)

        # 4. Віднімання порогу шуму та зважування яскравості
        weights = np.maximum(0.0, roi_img - self.threshold)
        weights *= in_window  # Занулення пікселів поза локальним вікном піка

        sum_weights = np.sum(weights, axis=0)
        sum_weighted_y = np.sum(weights * y_indices, axis=0)

        # 5. Критерій надійності: достатня накопичена енергія у вікні
        valid_energy = valid_mask & (sum_weights >= self.min_intensity_sum)

        # Розрахунок центру мас (зваженого середнього) з переходом у глобальні координати
        v_subpixel_roi[valid_energy] = (
            sum_weighted_y[valid_energy] / sum_weights[valid_energy]
        ) + y_min

        # 6. Формування вихідних масивів для всієї ширини кадру
        u_coords = np.arange(width, dtype=np.int32)
        v_subpixel = np.full(width, np.nan, dtype=np.float32)
        v_subpixel[x_min:x_max] = v_subpixel_roi

        return u_coords, v_subpixel

    def draw_line_overlay(
        self,
        bgr_image: np.ndarray,
        u_coords: np.ndarray,
        v_subpixel: np.ndarray,
        color: tuple[int, int, int] = (0, 255, 0),
    ) -> np.ndarray:
        """Накладає вектор знайденої субпіксельної лінії поверх кольорового кадру."""
        output = bgr_image.copy()
        valid = ~np.isnan(v_subpixel)

        if not np.any(valid):
            return output

        # Отримуємо точки неперервних сегментів
        pts = np.column_stack((u_coords[valid], v_subpixel[valid])).astype(np.float32)

        # Малюємо точки субпіксельного профілю
        for pt in pts:
            x, y = int(round(pt[0])), int(round(pt[1]))
            if 0 <= x < output.shape[1] and 0 <= y < output.shape[0]:
                output[y, x] = color

        return output
