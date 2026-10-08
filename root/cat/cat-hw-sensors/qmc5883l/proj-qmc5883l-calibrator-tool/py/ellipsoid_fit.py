"""
ellipsoid_fit.py
Математичний модуль на базі NumPy для накопичення 3D-точок магнітного поля,
алгебраїчної апроксимації геометрії даних у формі еліпсоїда методом найменших квадратів (Least Squares),
обчислення вектора зміщення жорсткого заліза (Hard-Iron offset) та матриці
масштабування й повороту для корекції м'якого заліза (Soft-Iron matrix).
"""
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class EllipsoidFitError(Exception):
    """Виняток при помилках апроксимації еліпсоїда чи недостатній кількості вибірок."""
    pass


class EllipsoidFitter:
    """
    Клас для накопичення 3D-векторів магнітного поля, чисельного розрахунку
    калібрувальних коефіцієнтів Hard-Iron/Soft-Iron через МНК (np.linalg.lstsq)
    та відносної оцінки сферичного покриття.
    """

    def __init__(self, target_field_strength: float = 1.0) -> None:
        self.target_field_strength = target_field_strength
        self.points: List[Tuple[float, float, float]] = []
        self.hard_iron_offset: Optional[np.ndarray] = None
        self.soft_iron_matrix: Optional[np.ndarray] = None
        self.is_calibrated: bool = False
        self.fit_rmse: float = 0.0

    def add_point(self, x: float, y: float, z: float) -> None:
        """Додає нову вибірку 3D-вектора магнітного поля до накопичувального буфера."""
        self.points.append((x, y, z))

    def clear(self) -> None:
        """Очищає буфер накопичених вибірок та скидає стан калібрування."""
        self.points.clear()
        self.hard_iron_offset = None
        self.soft_iron_matrix = None
        self.is_calibrated = False
        self.fit_rmse = 0.0

    def get_sample_count(self) -> int:
        """Повертає поточну кількість накопичених 3D-вибірок."""
        return len(self.points)

    def evaluate_spatial_coverage(self) -> Dict[str, float]:
        """
        Оцінює рівномірність обертання компаса за покриттям 8 октантів
        відносно поточного центру мас накопиченої хмари точок.
        Повертає словник з відсотками покриття та оцінкою придатності даних.
        """
        if len(self.points) < 10:
            return {"coverage_pct": 0.0, "octants_filled": 0.0}

        pts = np.array(self.points)
        centroid = np.mean(pts, axis=0)
        centered = pts - centroid

        octant_counts = [0] * 8
        for p in centered:
            idx = (1 if p[0] >= 0 else 0) | ((1 if p[1] >= 0 else 0) << 1) | ((1 if p[2] >= 0 else 0) << 2)
            octant_counts[idx] += 1

        filled = sum(1 for c in octant_counts if c > 0)
        coverage_pct = (filled / 8.0) * 100.0

        return {
            "coverage_pct": coverage_pct,
            "octants_filled": float(filled),
            "min_octant_samples": float(min(octant_counts)),
        }

    def fit(self, min_samples: int = 100) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Виконує алгебраїчну апроксимацію 3D-хмари точок рівнянням еліпсоїда.
        Формула квадрики: A x^2 + B y^2 + C z^2 + 2D xy + 2E xz + 2F yz + 2G x + 2H y + 2I z = 1
        Розраховує вектор Hard-Iron (offset) та матрицю Soft-Iron (W_soft).
        """
        n = len(self.points)
        if n < min_samples:
            raise EllipsoidFitError(
                f"Недостатньо вибірок для калібрування: {n} (необхідно мінімум {min_samples})."
            )

        pts = np.array(self.points, dtype=np.float64)
        x = pts[:, 0]
        y = pts[:, 1]
        z = pts[:, 2]

        d_mat = np.column_stack([
            x**2, y**2, z**2,
            2.0 * x * y, 2.0 * x * z, 2.0 * y * z,
            2.0 * x, 2.0 * y, 2.0 * z
        ])

        rhs = np.ones(n, dtype=np.float64)

        try:
            coeff, residuals, rank, singular_values = np.linalg.lstsq(d_mat, rhs, rcond=None)
        except np.linalg.LinAlgError as e:
            raise EllipsoidFitError(f"Помилка розв’язання МНК для еліпсоїда: {e}") from e

        if len(coeff) < 9:
            raise EllipsoidFitError("Неможливо обчислити коефіцієнти квадрики.")

        a_mat = np.array([
            [coeff[0], coeff[3], coeff[4]],
            [coeff[3], coeff[1], coeff[5]],
            [coeff[4], coeff[5], coeff[2]]
        ], dtype=np.float64)

        v_g = np.array([coeff[6], coeff[7], coeff[8]], dtype=np.float64)

        try:
            offset = -np.linalg.solve(a_mat, v_g)
        except np.linalg.LinAlgError as e:
            raise EllipsoidFitError(f"Матриця квадрики вироджена, неможливо знайти центр: {e}") from e

        c_scale = 1.0 - float(np.dot(v_g, offset))
        if c_scale <= 0:
            raise EllipsoidFitError(f"Некоректний коефіцієнт масштабування еліпсоїда c_scale={c_scale} <= 0.")

        m_mat = a_mat / c_scale

        evals, evecs = np.linalg.eigh(m_mat)

        if np.any(evals <= 0):
            raise EllipsoidFitError("Матриця еліпсоїда не є додатно визначеною (не еліпсоїд).")

        w_soft = evecs @ np.diag(np.sqrt(evals)) @ evecs.T

        w_soft *= self.target_field_strength

        self.hard_iron_offset = offset
        self.soft_iron_matrix = w_soft
        self.is_calibrated = True

        calibrated_pts = self.calibrate_batch(pts)
        norms = np.linalg.norm(calibrated_pts, axis=1)
        self.fit_rmse = float(np.sqrt(np.mean((norms - self.target_field_strength) ** 2)))

        logging.info(f"Калібрування еліпсоїда успішно виконано (RMSE={self.fit_rmse:.6f}).")
        logging.info(f"Hard-Iron offset (bx, by, bz): [{offset[0]:.2f}, {offset[1]:.2f}, {offset[2]:.2f}]")

        return self.hard_iron_offset, self.soft_iron_matrix, self.fit_rmse

    def calibrate_point(self, raw_point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Застосовує розраховані коефіцієнти до однієї 3D-точки."""
        if not self.is_calibrated or self.hard_iron_offset is None or self.soft_iron_matrix is None:
            raise EllipsoidFitError("Модель еліпсоїда ще не відкалібрована.")

        vec = np.array(raw_point, dtype=np.float64) - self.hard_iron_offset
        calib_vec = self.soft_iron_matrix @ vec
        return float(calib_vec[0]), float(calib_vec[1]), float(calib_vec[2])

    def calibrate_batch(self, raw_points: np.ndarray) -> np.ndarray:
        """Застосовує розраховані коефіцієнти до масиву (N x 3) 3D-точок."""
        if not self.is_calibrated or self.hard_iron_offset is None or self.soft_iron_matrix is None:
            raise EllipsoidFitError("Модель еліпсоїда ще не відкалібрована.")

        centered = raw_points - self.hard_iron_offset
        return centered @ self.soft_iron_matrix.T
