# Steinmetz Core Loss Calculator (Python implementation)
import math
import scipy.special

class SteinmetzCalculator:
    def __init__(self, k: float, alpha: float, beta: float):
        self.k = k
        self.alpha = alpha
        self.beta = beta

    def get_k_i(self) -> float:
        """Calculate modified material parameter k_i for iSE"""
        term1 = (2.0 * math.pi) ** (self.alpha - 1.0)
        term2 = 2.0 ** (self.beta - self.alpha + 1.0)
        beta_val = scipy.special.beta((self.alpha + 1.0) / 2.0, 0.5)
        return self.k / (term1 * term2 * beta_val)

    def calculate_ose(self, freq_hz: float, b_peak_tesla: float) -> float:
        """Calculate classic OSE loss density (W/m^3)"""
        return self.k * (freq_hz ** self.alpha) * (b_peak_tesla ** self.beta)

    def calculate_ise(self, b_samples: list[float], period_sec: float) -> float:
        """Calculate iSE loss density (W/m^3) for arbitrary B(t) array"""
        if len(b_samples) < 2 or period_sec <= 0:
            return 0.0
            
        dt = period_sec / (len(b_samples) - 1)
        delta_b = max(b_samples) - min(b_samples)
        if delta_b <= 0:
            return 0.0

        k_i = self.get_k_i()
        integral_sum = 0.0
        for i in range(len(b_samples) - 1):
            db_dt = (b_samples[i + 1] - b_samples[i]) / dt
            integral_sum += (abs(db_dt) ** self.alpha) * dt

        avg_integral = integral_sum / period_sec
        return k_i * avg_integral * (delta_b ** (self.beta - self.alpha))

# Приклад використання
if __name__ == "__main__":
    calc = SteinmetzCalculator(k=16.9, alpha=1.25, beta=2.55)
    f_hz = 100000.0
    b_pk = 0.1
    
    p_ose = calc.calculate_ose(f_hz, b_pk)
    print(f"OSE Loss Density: {p_ose:.2f} W/m^3 ({p_ose/1000:.2f} mW/cm^3)")
