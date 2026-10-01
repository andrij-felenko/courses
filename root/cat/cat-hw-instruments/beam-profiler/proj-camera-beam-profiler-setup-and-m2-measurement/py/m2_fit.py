import numpy as np


class M2CausticFitter:
    """Квадратична регресія моментних діаметрів D4σ(z) уздовж осі Z
    та розрахунок фактора якості лазерного пучка M² за стандартом ISO 11146.
    """

    def __init__(self, wavelength_nm: float = 632.8):
        """Параметри:
        wavelength_nm: Довжина хвилі лазерного випромінювання в нанометрах.
        """
        self.wavelength_um = wavelength_nm / 1000.0

    def fit_caustic(self, z_positions_mm: np.ndarray, diameters_um: np.ndarray) -> dict:
        """Виконує апроксимацію каустики d²(z) = A + B*z + C*z² поліномом другого порядку.

        Параметри:
            z_positions_mm: Масив позицій вимірювань уздовж осі Z в міліметрах.
            diameters_um: Масив виміряних моментних діаметрів D4σ в мікрометрах.

        Повертає словник з параметрами M², d0, z0, zR та кутом розбіжності.
        """
        if len(z_positions_mm) < 5:
            raise ValueError("Стандарт ISO 11146 вимагає щонайменше 10 площин вимірювання (мінімум 5 для базової апроксимації).")

        z = np.asarray(z_positions_mm, dtype=np.float64)
        d = np.asarray(diameters_um, dtype=np.float64)

        # Квадратична регресія для квадрованих діаметрів: d²(z) = C*z² + B*z + A
        poly_coeffs = np.polyfit(z, d ** 2, 2)
        C, B, A = poly_coeffs[0], poly_coeffs[1], poly_coeffs[2]

        if C <= 0:
            raise ValueError("Коефіцієнт кривини C повинен бути додатним для гіперболічної каустики.")

        # Позиція перетяжки (мінімуму каустики)
        z0_mm = -B / (2.0 * C)

        # Мінімальний діаметр перетяжки d0
        d02 = A - (B ** 2) / (4.0 * C)
        if d02 <= 0:
            raise ValueError("Фізично неможливе значення квадрата діаметра перетяжки.")
        d0_um = np.sqrt(d02)

        # Кут розбіжності theta (в мілірадіанах)
        # Оскільки z у мм, а d у мкм, sqrt(C) дає кут у мрад
        theta_mrad = np.sqrt(C)

        # Довжина Релея zR в мм
        zR_mm = d0_um / theta_mrad

        # Фактор якості пучка M² за ISO 11146: M² = (pi * d0 * theta) / (4 * lambda)
        theta_rad = theta_mrad / 1000.0
        m2 = (np.pi * d0_um * theta_rad) / (4.0 * self.wavelength_um)

        return {
            "M2": m2,
            "d0_um": d0_um,
            "z0_mm": z0_mm,
            "zR_mm": zR_mm,
            "theta_mrad": theta_mrad,
            "poly_coeffs": (C, B, A)
        }
