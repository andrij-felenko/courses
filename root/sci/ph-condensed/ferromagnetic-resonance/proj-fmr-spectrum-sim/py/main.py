import math

class FMRSimulator:
    def __init__(self, ms_ka_m=800.0, g_factor=2.10, alpha=0.007, dh0_oe=5.0):
        # ms_ka_m: намагніченість (кА/м), g_factor: фактор Ланде
        # alpha: параметр Гільберта, dh0_oe: неоднорідне уширення (Ерстед)
        self.ms = ms_ka_m * 1000.0  # А/м
        self.g = g_factor
        self.alpha = alpha
        self.dh0 = dh0_oe
        # γ / (2π) у ГГц/Тл: γ = g * e / (2 * m_e)
        self.gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * math.pi * 1e9)

    def kittel_inplane_field(self, freq_ghz):
        # Обчислення резонансного поля H_r для плівки у площині: f = γ √(H_r (H_r + M_s))
        # У термінах B_r (Тл): (f / γ)² = B_r * (B_r + μ0 M_s)
        mu0_ms = 4.0 * math.pi * 1e-7 * self.ms
        f_g = freq_ghz / self.gamma_ghz_t
        # Квадратне рівняння: B_r² + μ0 M_s B_r - (f/γ)² = 0
        b_r = (-mu0_ms + math.sqrt(mu0_ms**2 + 4.0 * f_g**2)) / 2.0
        return b_r * 10000.0  # перетворення у Гауси / Ерстеди

    def linewidth(self, freq_ghz):
        # ΔH(f) = ΔH0 + (2 α / γ) * 2π f
        # У Ерстедах: (2 * alpha * f) / (gamma / 2π) * 1000
        return self.dh0 + (2.0 * self.alpha * freq_ghz * 1000.0) / self.gamma_ghz_t

    def generate_spectrum(self, freq_ghz, h_min_oe, h_max_oe, points=500):
        hr = self.kittel_inplane_field(freq_ghz)
        dh = self.linewidth(freq_ghz)
        step = (h_max_oe - h_min_oe) / (points - 1)

        fields, chi_pp, deriv = [], [], []
        for i in range(points):
            h = h_min_oe + i * step
            fields.append(h)
            # Лоренціан поглинання
            denom = (h**2 - hr**2)**2 + (dh * h)**2
            val = (dh * h) / denom if denom != 0 else 0
            chi_pp.append(val)

        # Чисельна похідна dP/dH
        for i in range(points):
            if i == 0:
                d = (chi_pp[1] - chi_pp[0]) / step
            elif i == points - 1:
                d = (chi_pp[-1] - chi_pp[-2]) / step
            else:
                d = (chi_pp[i+1] - chi_pp[i-1]) / (2.0 * step)
            deriv.append(d)

        return fields, chi_pp, deriv

def fit_gilbert_damping(freqs_ghz, linewidths_oe, g_factor=2.10):
    n = len(freqs_ghz)
    if n < 2:
        raise ValueError("Потрібно принаймні 2 виміри для лінійного фітування")

    sum_f = sum(freqs_ghz)
    sum_dh = sum(linewidths_oe)
    sum_ff = sum(f*f for f in freqs_ghz)
    sum_fdh = sum(f*dh for f, dh in zip(freqs_ghz, linewidths_oe))

    slope = (n * sum_fdh - sum_f * sum_dh) / (n * sum_ff - sum_f**2)
    dh0 = (sum_dh - slope * sum_f) / n

    gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * math.pi * 1e9)
    # slope = (2 * alpha / gamma) * 1000  => alpha = slope * gamma / 2000
    alpha = (slope * gamma_ghz_t) / 2000.0

    return alpha, dh0

if __name__ == "__main__":
    sim = FMRSimulator(ms_ka_m=800.0, g_factor=2.08, alpha=0.0065, dh0_oe=4.5)
    f_test = 9.5 # ГГц (X-band)
    hr = sim.kittel_inplane_field(f_test)
    dh = sim.linewidth(f_test)
    print(f"Частота: {f_test} ГГц => Резонансне поле: {hr:.2f} Ое, Ширина лінії: {dh:.2f} Ое")

    freqs = [4.0, 8.0, 12.0, 16.0, 20.0]
    dhs = [sim.linewidth(f) for f in freqs]
    alpha_fit, dh0_fit = fit_gilbert_damping(freqs, dhs, g_factor=2.08)
    print(f"Фітування: alpha = {alpha_fit:.6f}, ΔH0 = {dh0_fit:.2f} Ое")
