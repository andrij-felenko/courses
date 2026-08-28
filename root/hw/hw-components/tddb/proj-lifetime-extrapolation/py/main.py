import math

class TDDBLifetimeCalculator:
    """Калькулятор екстраполяції ресурсу діелектрика TDDB."""
    KB_EV = 8.617333262145e-5  # Постійна Больцмана в еВ/К

    def __init__(self, t_ox_nm, a_test_cm2, a_chip_cm2):
        self.t_ox_nm = t_ox_nm
        self.a_test = a_test_cm2
        self.a_chip = a_chip_cm2

    @staticmethod
    def median_rank(i, n):
        """Наближення Бернарда для медіанних рангів кумулятивної ймовірності."""
        return (i - 0.3) / (n + 0.4)

    def fit_weibull(self, t_bd_samples):
        """Лінійна регресія в координатах Вейбула: ln(-ln(1 - F)) vs ln(t)."""
        samples = sorted(t_bd_samples)
        n = len(samples)
        x_vals = []
        y_vals = []

        for i, t in enumerate(samples, start=1):
            f = self.median_rank(i, n)
            w = math.log(-math.log(1.0 - f))
            x_vals.append(math.log(t))
            y_vals.append(w)

        # МНК лінійної регресії Y = a * X + b
        n_pts = len(x_vals)
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xx = sum(x * x for x in x_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))

        slope = (n_pts * sum_xy - sum_x * sum_y) / (n_pts * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n_pts

        beta = slope
        eta = math.exp(-intercept / beta)
        return beta, eta

    def fit_power_law_voltage(self, stress_points):
        """Підгонка степеневої моделі: ln(eta) = ln(C0) - n_v * ln(V).
        stress_points: список кортежів (voltage, eta) при фіксованій T."""
        x_vals = [math.log(v) for v, _ in stress_points]
        y_vals = [math.log(eta) for _, eta in stress_points]

        n_pts = len(x_vals)
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xx = sum(x * x for x in x_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))

        slope = (n_pts * sum_xy - sum_x * sum_y) / (n_pts * sum_xx - sum_x * sum_x)
        n_v = -slope
        c0 = math.exp((sum_y - slope * sum_x) / n_pts)
        return n_v, c0

    def calculate_acceleration_factor(self, v_stress, v_op, n_v, t_stress_c, t_op_c, ea_ev):
        """Розрахунок загального коефіцієнта прискорення AF = AF_V * AF_T."""
        # Напругове прискорення
        af_v = (v_stress / v_op) ** n_v

        # Температурне прискорення за Арреніусом
        t_stress_k = t_stress_c + 273.15
        t_op_k = t_op_c + 273.15
        delta_inv_t = (1.0 / t_op_k) - (1.0 / t_stress_k)
        af_t = math.exp((ea_ev / self.KB_EV) * delta_inv_t)

        return af_v * af_t

    def extrapolate_chip_lifetime(self, eta_stress, af_total, beta, target_f):
        """Екстраполяція характеристичного часу та часу досягнення браку F для чіпа."""
        # 1. Характеристичний час одиночного транзистора при робочому режимі
        eta_op_test = eta_stress * af_total

        # 2. Масштабування площі: чіп містить у мільйони разів більшу площу діелектрика
        area_scale_factor = (self.a_test / self.a_chip) ** (1.0 / beta)
        eta_op_chip = eta_op_test * area_scale_factor

        # 3. Розрахунок часу до накопичення частки браку target_f
        w_target = -math.log(1.0 - target_f)
        t_target_sec = eta_op_chip * (w_target ** (1.0 / beta))
        t_target_years = t_target_sec / (365.25 * 24 * 3600)

        return eta_op_chip, t_target_years


# Демонстраційний розрахунок
if __name__ == "__main__":
    calc = TDDBLifetimeCalculator(t_ox_nm=1.4, a_test_cm2=1e-6, a_chip_cm2=0.05)

    # Вибірка виміряних часів пробою (секунди) при 2.6 В і 125 °C
    samples_2_6v = [
        450.2, 780.5, 920.1, 1105.4, 1340.8, 1560.2, 1780.9, 1950.0,
        2240.3, 2510.6, 2890.4, 3210.1, 3650.8, 4120.5, 4890.2
    ]

    beta, eta_stress = calc.fit_weibull(samples_2_6v)
    print(f"Оцінений нахил Вейбула β: {beta:.2f}")
    print(f"Характеристичний час стресу η_stress: {eta_stress:.1f} с")

    # Дані підгонки за напругою (напруга, характеристичний час)
    stress_curve = [(2.8, 450.0), (2.6, eta_stress), (2.4, 15400.0)]
    n_v, _ = calc.fit_power_law_voltage(stress_curve)
    print(f"Показник напругового прискорення n_v: {n_v:.1f}")

    # Екстраполяція на робочі умови (0.85 В, 85 °C, ціль 100 ppm)
    af = calc.calculate_acceleration_factor(
        v_stress=2.6, v_op=0.85, n_v=n_v,
        t_stress_c=125.0, t_op_c=85.0, ea_ev=0.75
    )
    print(f"Загальний коефіцієнт прискорення AF: {af:.2e}")

    eta_chip, t_100ppm_years = calc.extrapolate_chip_lifetime(
        eta_stress=eta_stress, af_total=af, beta=beta, target_f=0.0001
    )
    print(f"Характеристичний час чіпа: {eta_chip:.2e} с")
    print(f"Термін служби чіпа до 100 ppm браку: {t_100ppm_years:.2e} років")
