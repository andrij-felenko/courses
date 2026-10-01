import numpy as np


class BeamProfiler:
    """Обробка зображень КМОН-сенсора, віднімання темного кадру,
    порогове фільтрування та обчислення моментів D4σ за стандартом ISO 11146.
    """

    def __init__(self, threshold_factor: float = 0.01):
        """Параметри:
        threshold_factor: Відносна величина порогу фонового шуму (за замовчуванням 1% від максимуму).
        """
        self.threshold_factor = threshold_factor

    def subtract_dark_frame(self, image: np.ndarray, dark_frame: np.ndarray) -> np.ndarray:
        """Віднімає темний кадр від сигнального зображення з відсіканням від'ємних значений."""
        img_float = image.astype(np.float64)
        dark_float = dark_frame.astype(np.float64)
        subtracted = np.maximum(0.0, img_float - dark_float)
        return subtracted

    def apply_threshold(self, image: np.ndarray) -> np.ndarray:
        """Обнуляє фоновий шум нижче відносного порогу для запобігання викривленню моментів другого порядку."""
        max_val = np.max(image)
        threshold = max_val * self.threshold_factor
        filtered = np.where(image >= threshold, image, 0.0)
        return filtered

    def compute_moments(self, image: np.ndarray, pixel_size_um: float = 3.45) -> dict:
        """Обчислює центроїд (перші моменти) та моментні діаметри D4σ (другі центральні моменти).

        Параметри:
            image: 2D-матриця інтенсивності після віднімання темного кадру та фільтрації.
            pixel_size_um: Розмір пікселя КМОН-сенсора в мікрометрах.

        Повертає словник з параметрами пучка.
        """
        total_intensity = np.sum(image)
        if total_intensity <= 0:
            raise ValueError("Сумарна інтенсивність кадру дорівнює нулю або від'ємна.")

        height, width = image.shape
        x_indices = np.arange(width)
        y_indices = np.arange(height)
        grid_x, grid_y = np.meshgrid(x_indices, y_indices)

        # Перші моменти — координати центроїда в пікселях
        centroid_x = np.sum(grid_x * image) / total_intensity
        centroid_y = np.sum(grid_y * image) / total_intensity

        # Другі центральні моменти (дисперсії і коваріація)
        dx_grid = grid_x - centroid_x
        dy_grid = grid_y - centroid_y

        sigma_x2 = np.sum((dx_grid ** 2) * image) / total_intensity
        sigma_y2 = np.sum((dy_grid ** 2) * image) / total_intensity
        sigma_xy = np.sum(dx_grid * dy_grid * image) / total_intensity

        # Моментні діаметри D4σ за стандартом ISO 11146 (4 * sigma)
        sigma_x = np.sqrt(max(0.0, sigma_x2))
        sigma_y = np.sqrt(max(0.0, sigma_y2))

        d4s_x_um = 4.0 * sigma_x * pixel_size_um
        d4s_y_um = 4.0 * sigma_y * pixel_size_um

        return {
            "total_intensity": total_intensity,
            "centroid_x_px": centroid_x,
            "centroid_y_px": centroid_y,
            "dx_um": d4s_x_um,
            "dy_um": d4s_y_um,
            "sigma_x_px": sigma_x,
            "sigma_y_px": sigma_y,
            "sigma_xy_px": sigma_xy
        }
