import math
import cmath
from typing import List, Tuple

class SkinEffectAnalytical:
    """Аналітичний розрахунок скін-ефекту для циліндричного провідника."""
    
    def __init__(self, sigma: float = 5.8e7, mu_r: float = 1.0):
        self.sigma = sigma
        self.mu_r = mu_r
        self.mu0 = 4.0 * math.pi * 1e-7

    def skin_depth(self, freq_hz: float) -> float:
        """Обчислення глибини скін-шару (м)."""
        omega = 2.0 * math.pi * freq_hz
        return math.sqrt(2.0 / (omega * (self.mu0 * self.mu_r) * self.sigma))

    @staticmethod
    def bessel_i0(z: complex) -> complex:
        """Модифікована функція Бесселя I_0(z) через ряд Тейлора."""
        sum_val = complex(1.0, 0.0)
        term = complex(1.0, 0.0)
        z_sq_4 = (z * z) / 4.0
        for k in range(1, 60):
            term = term * z_sq_4 / (k * k)
            sum_val += term
            if abs(term) < 1e-12 * abs(sum_val):
                break
        return sum_val

    @staticmethod
    def bessel_i1(z: complex) -> complex:
        """Модифікована функція Бесселя I_1(z) через ряд Тейлора."""
        sum_val = z / 2.0
        term = z / 2.0
        z_sq_4 = (z * z) / 4.0
        for k in range(1, 60):
            term = term * z_sq_4 / (k * (k + 1))
            sum_val += term
            if abs(term) < 1e-12 * abs(sum_val):
                break
        return sum_val

    def rac_rdc_ratio(self, radius_m: float, freq_hz: float) -> float:
        """Обчислення відношення R_AC / R_DC."""
        delta = self.skin_depth(freq_hz)
        x = radius_m / delta
        
        if x < 0.1:
            return 1.0 + (1.0 / 48.0) * (x ** 4)
        if x > 15.0:
            return 0.5 * x + 0.25 + 0.094 / x

        k = complex(1.0 / delta, 1.0 / delta)
        ka = k * radius_m
        i0 = self.bessel_i0(ka)
        i1 = self.bessel_i1(ka)
        ratio = (ka / 2.0) * (i0 / i1)
        return ratio.real


class SkinEffectFDMSolver:
    """1D Сінченно-різницевий розв'язувач (FDM) для пластини з методом Томаса."""
    
    def __init__(self, thickness_m: float, nodes: int = 200):
        self.d = thickness_m
        self.n = nodes
        self.dx = thickness_m / (nodes - 1)

    def solve_field(self, freq_hz: float, sigma_profile: List[float], mu_r: float = 1.0) -> List[complex]:
        """Розв'язок СЛАР методом прогонки (Thomas Algorithm)."""
        mu0 = 4.0 * math.pi * 1e-7
        omega = 2.0 * math.pi * freq_hz
        n = self.n
        dx = self.dx
        
        a = [complex(0, 0)] * n
        b = [complex(0, 0)] * n
        c = [complex(0, 0)] * n
        rhs = [complex(0, 0)] * n
        
        # Граничні умови Діріхле на поверхнях
        b[0] = complex(1.0, 0.0)
        rhs[0] = complex(1.0, 0.0)
        b[n - 1] = complex(1.0, 0.0)
        rhs[n - 1] = complex(1.0, 0.0)
        
        for i in range(1, n - 1):
            sigma_i = sigma_profile[i]
            a[i] = complex(1.0, 0.0)
            c[i] = complex(1.0, 0.0)
            b[i] = - complex(2.0, omega * (mu0 * mu_r) * sigma_i * (dx ** 2))
            rhs[i] = complex(0.0, 0.0)
            
        # Прямий хід прогонки
        c_prime = [complex(0, 0)] * n
        d_prime = [complex(0, 0)] * n
        
        c_prime[0] = c[0] / b[0]
        d_prime[0] = rhs[0] / b[0]
        
        for i in range(1, n):
            temp = b[i] - a[i] * c_prime[i - 1]
            c_prime[i] = c[i] / temp
            d_prime[i] = (rhs[i] - a[i] * d_prime[i - 1]) / temp
            
        # Зворотний хід прогонки
        e_field = [complex(0, 0)] * n
        e_field[n - 1] = d_prime[n - 1]
        for i in range(n - 2, -1, -1):
            e_field[i] = d_prime[i] - c_prime[i] * e_field[i + 1]
            
        return e_field

    def calculate_rac_rdc(self, freq_hz: float, sigma_profile: List[float], mu_r: float = 1.0) -> float:
        """Обчислення втрат потужності та відношення R_AC / R_DC."""
        e_field = self.solve_field(freq_hz, sigma_profile, mu_r)
        
        # Обчислення втрат змінного струму: P_AC = integral(sigma * |E|^2 dx)
        p_ac = 0.0
        total_current = complex(0.0, 0.0)
        sigma_dc_sum = 0.0
        
        for i in range(self.n):
            sig = sigma_profile[i]
            val = abs(e_field[i]) ** 2
            p_ac += sig * val * self.dx
            total_current += sig * e_field[i] * self.dx
            sigma_dc_sum += sig * self.dx
            
        i_abs_sq = abs(total_current) ** 2
        r_ac = p_ac / i_abs_sq
        r_dc = 1.0 / sigma_dc_sum
        return r_ac / r_dc


def main():
    wire_radius = 0.001  # 1 мм
    freqs = [50.0, 1e3, 10e3, 100e3, 1e6, 10e6]
    
    calc = SkinEffectAnalytical(sigma=5.8e7, mu_r=1.0)
    print("Частота (Гц)   | Скін-шар (мкм) | R_AC / R_DC (Бессель)")
    print("-" * 55)
    for f in freqs:
        delta = calc.skin_depth(f)
        ratio = calc.rac_rdc_ratio(wire_radius, f)
        print(f"{f:-14.1e} | {delta * 1e6:-14.2f} | {ratio:-12.4f}")

if __name__ == "__main__":
    main()
