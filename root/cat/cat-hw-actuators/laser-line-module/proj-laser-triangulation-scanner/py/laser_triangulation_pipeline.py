"""Головний конвеєр тріангуляційного вимірювання рельєфу поверхні лазерною смугою.

Поєднує диференційне віднімання фонової засвітки (Laser ON / Laser OFF),
субпіксельне детектування лінії (COG), тріангуляційний перерахунок у міліметри
та побудову карти рельєфу висот у реальному часі.
"""

from __future__ import annotations

import cv2
import numpy as np

from cog_extractor import SubpixelCogDetector
from triangulation_calibrator import TriangulationHeightMapper


class DifferentialLaserFilter:
    """Диференційне віднімання синхронізованих пар кадрів зі спалахом лазера й без нього

    для пригнічення зовнішнього фонового освітлення приміщення.
    """

    def __init__(self, clip_negative: bool = True) -> None:
        """Ініціалізує фільтр.

        Параметри:
            clip_negative: Чи обрізати від'ємні різниці яскравості до 0 (uint8).
        """
        self.clip_negative = clip_negative

    def filter(self, laser_on_frame: np.ndarray, laser_off_frame: np.ndarray) -> np.ndarray:
        """Обчислює різницевий кадр (Laser ON мінус Laser OFF).

        Параметри:
            laser_on_frame: Кадр, освітлений лазером і зовнішнім світлом.
            laser_off_frame: Кадр суто із зовнішнім фоновим світлом (лазер вимкнено).

        Повертає:
            diff: Одноканальне напівтонове зображення з виділеним сигналом лазера.
        """
        # Перетворення напівтонових каналів
        on_gray = (
            cv2.cvtColor(laser_on_frame, cv2.COLOR_BGR2GRAY)
            if laser_on_frame.ndim == 3
            else laser_on_frame
        )
        off_gray = (
            cv2.cvtColor(laser_off_frame, cv2.COLOR_BGR2GRAY)
            if laser_off_frame.ndim == 3
            else laser_off_frame
        )

        # Безпечне віднімання без переповнення діапазону uint8
        if self.clip_negative:
            # cv2.subtract автоматично насичує результат до [0, 255]
            diff = cv2.subtract(on_gray, off_gray)
        else:
            diff_int16 = on_gray.astype(np.int16) - off_gray.astype(np.int16)
            diff = np.clip(diff_int16, 0, 255).astype(np.uint8)

        return diff


class LaserTriangulationPipeline:
    """Головний конвеєр координації компонентів тріангуляційної системи."""

    def __init__(
        self,
        frame_width: int = 640,
        frame_height: int = 480,
        pixel_size_x_mm: float = 0.05,
        scale_z_mm_per_px: float = 0.04,
    ) -> None:
        self.width = frame_width
        self.height = frame_height

        self.diff_filter = DifferentialLaserFilter(clip_negative=True)
        self.detector = SubpixelCogDetector(
            threshold=20.0,
            window_radius=7,
            min_peak_value=35.0,
            min_intensity_sum=80.0,
        )
        self.calibrator = TriangulationHeightMapper(
            pixel_size_x_mm=pixel_size_x_mm,
            default_scale_z_mm_per_px=scale_z_mm_per_px,
        )

        # Буфер для накопичення карти рельєфу (профілограма під час руху об'єкта)
        self.max_scan_history: int = 200
        self.height_map_buffer: list[np.ndarray] = []

    def generate_synthetic_frame_pair(
        self,
        step_height_mm: float = 5.0,
        step_width_px: int = 160,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Генерує реалістичну синтетичну пару кадрів для тестування без фізичної камери.

        Моделює:
        - Паразитне фонове світло (градієнт від вікна + яскрава лампа в кутку).
        - Базову поверхню столу на v = 260 px.
        - Еталонну сходинку висотою step_height_mm у центрі смуги.
        - Гаусів профіль лінії лазера товщиною ~4 px зі спекл-шумом.
        """
        h, w = self.height, self.width

        # 1. Фонове освітлення (лампа + загальний градієнт)
        y_grid, x_grid = np.mgrid[0:h, 0:w]
        ambient = (
            50.0
            + 30.0 * (x_grid / w)
            + 60.0 * np.exp(-((x_grid - 100) ** 2 + (y_grid - 100) ** 2) / 30000.0)
        )
        ambient += np.random.normal(0.0, 2.0, size=(h, w))
        frame_laser_off = np.clip(ambient, 0, 255).astype(np.uint8)

        # 2. Модель геометрії лазерної смуги
        # Базова площина на висоті 0 мм розташована на піксельній координаті v = 260
        v_base = 260.0 + 2.0 * np.sin(x_grid[0, :] / 50.0)  # Легка нерівність базової площини

        # Сходинка в центрі: висота step_height_mm
        # Зсув лінії вгору: delta_v = step_height_mm / scale_z
        delta_v_true = step_height_mm / self.calibrator.default_scale_z
        center_x = w // 2
        step_mask = np.abs(x_grid[0, :] - center_x) < (step_width_px // 2)

        v_line = v_base.copy()
        v_line[step_mask] -= delta_v_true

        # 3. Гаусів профіль пучка вздовж кожного стовпця
        beam_sigma = 1.8  # радіус перетяжки пучка
        laser_intensity = np.zeros((h, w), dtype=np.float32)

        for col in range(w):
            center_v = v_line[col]
            column_y = y_grid[:, col]
            # Гаусова яскравість лінії
            profile = 180.0 * np.exp(-0.5 * ((column_y - center_v) / beam_sigma) ** 2)
            laser_intensity[:, col] = profile

        # Додавання спекл-шуму та квантування
        speckle = np.random.uniform(0.85, 1.15, size=(h, w))
        laser_total = ambient + laser_intensity * speckle
        frame_laser_on = np.clip(laser_total, 0, 255).astype(np.uint8)

        return frame_laser_on, frame_laser_off

    def process_frame_pair(
        self,
        frame_on: np.ndarray,
        frame_off: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Виконує повний цикл обробки пари кадрів.

        Повертає:
            diff_img: Різницеве зображення після видалення фону.
            u_coords: Горизонтальні координати стовпців.
            x_mm: Фізичні координати вздовж лінії (мм).
            z_mm: Обчислена висота рельєфу (мм).
        """
        # Крок 1: Диференційне віднімання фонової засвітки
        diff_img = self.diff_filter.filter(frame_on, frame_off)

        # Крок 2: Субпіксельний пошук центру мас (COG)
        u_coords, v_subpixel = self.detector.detect_subpixel_line(diff_img)

        # Крок 3: Тріангуляційний перерахунок у метричні величини
        x_mm, z_mm, _ = self.calibrator.pixel_to_metric(u_coords, v_subpixel)

        # Збереження у буфер сканування
        self.height_map_buffer.append(z_mm.copy())
        if len(self.height_map_buffer) > self.max_scan_history:
            self.height_map_buffer.pop(0)

        return diff_img, u_coords, x_mm, z_mm

    def render_profile_plot(
        self,
        x_mm: np.ndarray,
        z_mm: np.ndarray,
        plot_width: int = 640,
        plot_height: int = 240,
    ) -> np.ndarray:
        """Створює наочний 2D-графік виміряного профілю висоти Z(X)."""
        plot = np.full((plot_height, plot_width, 3), 250, dtype=np.uint8)

        # Координатна сітка
        cv2.line(plot, (40, 20), (40, plot_height - 30), (200, 200, 200), 1)
        cv2.line(plot, (40, plot_height - 30), (plot_width - 20, plot_height - 30), (200, 200, 200), 1)

        valid = ~np.isnan(z_mm)
        if not np.any(valid):
            cv2.putText(plot, "Linia ne vyiavleno", (60, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 200), 2)
            return plot

        z_valid = z_mm[valid]
        z_min, z_max = 0.0, max(10.0, float(np.nanmax(z_valid) * 1.2))

        # Перетворення (X, Z) в екранні координати графіка
        u_indices = np.arange(len(z_mm))[valid]
        px_x = 40 + (u_indices * (plot_width - 60) // len(z_mm)).astype(np.int32)
        px_y = (plot_height - 30 - ((z_valid - z_min) / (z_max - z_min + 1e-6) * (plot_height - 50))).astype(np.int32)

        pts = np.column_stack((px_x, px_y))
        cv2.polylines(plot, [pts], isClosed=False, color=(214, 87, 36), thickness=2)

        # Текстова розмітка
        max_h = float(np.nanmax(z_valid))
        mean_h = float(np.nanmean(z_valid))
        cv2.putText(plot, f"Max Z: {max_h:.2f} mm", (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 1)
        cv2.putText(plot, f"Mean Z: {mean_h:.2f} mm", (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 1)
        cv2.putText(plot, "0 mm", (5, plot_height - 26), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
        cv2.putText(plot, f"{z_max:.1f} mm", (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)

        return plot

    def render_height_map(self) -> np.ndarray:
        """Візуалізує накопичену поверхневу карту висот у псевдокольорах."""
        if not self.height_map_buffer:
            return np.zeros((100, self.width, 3), dtype=np.uint8)

        grid = np.array(self.height_map_buffer)  # форма (N, W)
        grid_clean = np.nan_to_num(grid, nan=0.0)

        z_max = max(1.0, float(np.max(grid_clean)))
        norm = np.clip((grid_clean / z_max) * 255.0, 0, 255).astype(np.uint8)
        color_map = cv2.applyColorMap(norm, cv2.COLORMAP_JET)

        return color_map

    def run_live_camera(self, camera_index: int = 0) -> None:
        """Запускає цикл захоплення з фізичної камери (якщо підключено).

        Для чергування спалахів лазера очікується зовнішній генератор стробу або
        апаратна синхронізація GPIO. У простому режимі виконує захоплення й аналіз.
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Помилка: не вдалося відкрити камеру з індексом {camera_index}.")
            return

        print("Запуск відеопотоку. Натисніть 'q' для виходу, 'b' для калібрування базової площини.")
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                u_coords, v_sub = self.detector.detect_subpixel_line(gray)
                x_mm, z_mm, _ = self.calibrator.pixel_to_metric(u_coords, v_sub)

                overlay = self.detector.draw_line_overlay(frame, u_coords, v_sub)
                plot = self.render_profile_plot(x_mm, z_mm)

                cv2.imshow("Laser Triangulation - Camera", overlay)
                cv2.imshow("Laser Triangulation - Profile Z(X)", plot)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("b"):
                    self.calibrator.calibrate_baseline(u_coords, v_sub)
                    print("Базову лінію перекалібровано!")
        finally:
            cap.release()
            cv2.destroyAllWindows()


def main() -> None:
    """Точка входу для демонстрації роботи конвеєра тріангуляції."""
    print("=== Лазерна тріангуляція: конвеєр обробки сигналу ===")
    pipeline = LaserTriangulationPipeline(frame_width=640, frame_height=480)

    # 1. Етап калібрування базової площини (нульового рівня столу)
    print("Калібрування базової площини столу...")
    base_on, base_off = pipeline.generate_synthetic_frame_pair(step_height_mm=0.0)
    diff_base = pipeline.diff_filter.filter(base_on, base_off)
    u_coords, v_base = pipeline.detector.detect_subpixel_line(diff_base)
    pipeline.calibrator.calibrate_baseline(u_coords, v_base, poly_order=1)
    print(f"Базову лінію відкалібровано. Центр: u = {pipeline.calibrator.u_center_px:.1f} px.")

    # 2. Моделювання сканування деталі зі сходинкою 6.0 мм
    print("Сканування дослідного об'єкта (еталонна сходинка 6.0 мм)...")
    frame_on, frame_off = pipeline.generate_synthetic_frame_pair(step_height_mm=6.0)

    _, _, x_mm, z_mm = pipeline.process_frame_pair(frame_on, frame_off)

    measured_step = float(np.nanmax(z_mm))
    print(f"Результат вимірювання висоти: {measured_step:.3f} мм (еталон: 6.000 мм).")
    print(f"Похибка тріангуляції: {abs(measured_step - 6.0):.4f} мм.")

    # 3. Формування підсумкового зображення профілю
    profile_plot = pipeline.render_profile_plot(x_mm, z_mm)
    print(f"Розмір графіка профілю: {profile_plot.shape[1]}x{profile_plot.shape[0]} px.")
    print("Обробку успішно завершено.")


if __name__ == "__main__":
    main()
