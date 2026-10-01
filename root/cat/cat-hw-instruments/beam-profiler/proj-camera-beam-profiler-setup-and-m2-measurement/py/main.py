import numpy as np
from beam_profiler import BeamProfiler
from m2_fit import M2CausticFitter


def generate_synthetic_frame(width: int, height: int, cx: float, cy: float, wx_px: float, wy_px: float, noise_level: float = 5.0) -> np.ndarray:
    """Генерує синтетичний 2D гаусів кадр із додаванням шуму."""
    x = np.arange(width)
    y = np.arange(height)
    gx, gy = np.meshgrid(x, y)

    gaussian = 200.0 * np.exp(-2.0 * (((gx - cx) / wx_px)**2 + ((gy - cy) / wy_px)**2))
    noise = np.random.poisson(noise_level, size=(height, width))
    frame = np.clip(gaussian + noise, 0, 255).astype(np.uint16)
    return frame


def main():
    print("=== Демонстрація аналізу лазерного пучка та розрахунку M² ===")

    # Параметри вимірювальної системи
    pixel_size_um = 3.45  # Розмір пікселя КМОН-сенсора
    wavelength_nm = 632.8  # He-Ne лазер (632.8 нм)

    profiler = BeamProfiler(threshold_factor=0.01)

    # Згенерований темний кадр (шум матриці при закритому апертурному затворі)
    dark_frame = np.full((512, 512), fill_value=5, dtype=np.uint16)

    # Експериментальні позиції вздовж осі Z (в міліметрах)
    z_positions = np.array([-50.0, -30.0, -15.0, -5.0, 0.0, 5.0, 15.0, 30.0, 50.0])

    # Ідеальні параметри перетяжки для синтезу вимірювань: d0 = 200 мкм, zR = 25 мм
    d0_true_um = 200.0
    zR_true_mm = 25.0

    measured_dx = []

    print("\n[1] Обробка кадрів у площинах Z...")
    for z in z_positions:
        # Розрахунок теоретичного діаметра пучка d(z) = d0 * sqrt(1 + (z/zR)²)
        d_z_um = d0_true_um * np.sqrt(1.0 + (z / zR_true_mm)**2)
        w_z_px = (d_z_um / 2.0) / pixel_size_um

        # Симуляція кадрів із центроїдом у центрі матриці (256, 256)
        raw_frame = generate_synthetic_frame(512, 512, 256.0, 256.0, w_z_px, w_z_px)

        # Віднімання темного кадру та фільтрація шуму
        subtracted = profiler.subtract_dark_frame(raw_frame, dark_frame)
        thresholded = profiler.apply_threshold(subtracted)

        # Розрахунок моментів D4σ
        moments = profiler.compute_moments(thresholded, pixel_size_um=pixel_size_um)
        measured_dx.append(moments["dx_um"])

        print(f"  Z = {z:6.1f} мм | Виміряний D4σ_x = {moments['dx_um']:6.2f} мкм | Центроїд: ({moments['centroid_x_px']:.1f}, {moments['centroid_y_px']:.1f}) px")

    measured_dx = np.array(measured_dx)

    # [2] Апроксимація каустики та розрахунок факторів за ISO 11146
    print("\n[2] Апроксимація каустики та розрахунок моментів за ISO 11146...")
    fitter = M2CausticFitter(wavelength_nm=wavelength_nm)
    results = fitter.fit_caustic(z_positions, measured_dx)

    print("\n--- Результати вимірювання M² ---")
    print(f"  Фактор якості пучка M²:        {results['M2']:.3f}")
    print(f"  Діаметр перетяжки d0:          {results['d0_um']:.2f} мкм")
    print(f"  Позиція фокуса z0:              {results['z0_mm']:.2f} мм")
    print(f"  Довжина Релея zR:              {results['zR_mm']:.2f} мм")
    print(f"  Кут розбіжності theta:         {results['theta_mrad']:.3f} мрад")


if __name__ == "__main__":
    main()
