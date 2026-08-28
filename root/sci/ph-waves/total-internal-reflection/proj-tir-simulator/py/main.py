import math

class FtirSimulator:
    def __init__(self, n1=1.50, n2=1.00, n3=1.50, lambda_nm=632.8, theta_deg=45.0):
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.lambda_nm = lambda_nm
        self.theta_deg = theta_deg
        
    def penetration_depth(self):
        theta_rad = math.radians(self.theta_deg)
        sin_t = math.sin(theta_rad)
        val = self.n1**2 * sin_t**2 - self.n2**2
        if val <= 0:
            raise ValueError("Кут падіння менший за критичний!")
        alpha = (2.0 * math.pi / self.lambda_nm) * math.sqrt(val)
        return 1.0 / alpha
        
    def transmission(self, gap_nm):
        if gap_nm <= 1e-9:
            return 1.0
        theta_rad = math.radians(self.theta_deg)
        sin_t = math.sin(theta_rad)
        cos_t = math.cos(theta_rad)
        
        val = self.n1**2 * sin_t**2 - self.n2**2
        if val <= 0:
            return 1.0
            
        alpha = (2.0 * math.pi / self.lambda_nm) * math.sqrt(val)
        num = (self.n1**2 - self.n2**2)**2
        den = 4.0 * self.n1**2 * val * cos_t**2
        C = num / den
        
        arg = alpha * gap_nm
        if arg > 35.0:
            return (4.0 / C) * math.exp(-2.0 * arg)
            
        sh_val = math.sinh(arg)
        return 1.0 / (1.0 + C * sh_val**2)

    def scan_gap(self, max_gap_nm=2000.0, steps=10):
        dp = self.penetration_depth()
        print(f"Показники: n1={self.n1}, n2={self.n2}, lambda={self.lambda_nm} нм, theta={self.theta_deg}°")
        print(f"Глибина проникнення dp = {dp:.2f} нм\n")
        print(f"{'Зазор d (нм)':<14} {'d / lambda':<14} {'T (пропускання)':<18} {'R (відбиття)':<18}")
        print("-" * 64)
        
        results = []
        for i in range(steps + 1):
            gap = i * (max_gap_nm / steps)
            T = self.transmission(gap)
            R = 1.0 - T
            results.append((gap, gap / self.lambda_nm, T, R))
            print(f"{gap:<14.1f} {gap / self.lambda_nm:<14.3f} {T:<18.6f} {R:<18.6f}")
        return results

if __name__ == "__main__":
    sim = FtirSimulator()
    sim.scan_gap()
