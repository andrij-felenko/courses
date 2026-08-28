import math

class ThinFilmSimulator:
    def __init__(self, n1=1.00, n2=1.33, n3=1.00):
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3

    @staticmethod
    def _cie_x_bar(l):
        t1 = (l - 442.0) / (16.0 if l < 442.0 else 22.0)
        t2 = (l - 599.0) / (38.0 if l < 599.0 else 32.0)
        t3 = (l - 501.0) / (24.0 if l < 501.0 else 22.0)
        return 0.362 * math.exp(-0.5 * t1**2) + 1.056 * math.exp(-0.5 * t2**2) - 0.065 * math.exp(-0.5 * t3**2)

    @staticmethod
    def _cie_y_bar(l):
        t1 = (l - 568.8) / (46.9 if l < 568.8 else 44.5)
        t2 = (l - 530.9) / (16.3 if l < 530.9 else 37.1)
        return 0.821 * math.exp(-0.5 * t1**2) + 0.286 * math.exp(-0.5 * t2**2)

    @staticmethod
    def _cie_z_bar(l):
        t1 = (l - 437.0) / (11.8 if l < 437.0 else 19.8)
        t2 = (l - 459.0) / (26.0 if l < 459.0 else 26.0)
        return 1.217 * math.exp(-0.5 * t1**2) + 0.681 * math.exp(-0.5 * t2**2)

    def calculate_reflectance(self, lambda_nm, d_nm, theta1_rad=0.0):
        sin_t2 = (self.n1 / self.n2) * math.sin(theta1_rad)
        if abs(sin_t2) > 1.0:
            return 1.0
        theta2_rad = math.asin(sin_t2)

        sin_t3 = (self.n2 / self.n3) * math.sin(theta2_rad)
        theta3_rad = math.asin(sin_t3) if abs(sin_t3) <= 1.0 else 0.0

        r12 = (self.n1 * math.cos(theta1_rad) - self.n2 * math.cos(theta2_rad)) / \
              (self.n1 * math.cos(theta1_rad) + self.n2 * math.cos(theta2_rad))
        r23 = (self.n2 * math.cos(theta2_rad) - self.n3 * math.cos(theta3_rad)) / \
              (self.n2 * math.cos(theta2_rad) + self.n3 * math.cos(theta3_rad))

        beta = (4.0 * math.pi * self.n2 * d_nm * math.cos(theta2_rad)) / lambda_nm

        num = r12**2 + r23**2 + 2.0 * r12 * r23 * math.cos(beta)
        den = 1.0 + r12**2 * r23**2 + 2.0 * r12 * r23 * math.cos(beta)
        return max(0.0, min(1.0, num / den))

    def simulate_hex_color(self, d_nm, theta1_rad=0.0):
        X, Y, Z, norm_y = 0.0, 0.0, 0.0, 0.0
        step = 5.0
        for l in [380.0 + i * step for i in range(int((780.0 - 380.0) / step) + 1)]:
            r_val = self.calculate_reflectance(l, d_nm, theta1_rad)
            xb, yb, zb = self._cie_x_bar(l), self._cie_y_bar(l), self._cie_z_bar(l)
            X += r_val * xb * step
            Y += r_val * yb * step
            Z += r_val * zb * step
            norm_y += yb * step

        if norm_y > 0.0:
            X, Y, Z = X / norm_y, Y / norm_y, Z / norm_y

        r_lin =  3.2406 * X - 1.5372 * Y - 0.4986 * Z
        g_lin = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
        b_lin =  0.0557 * X - 0.2040 * Y + 1.0570 * Z

        def gamma(val):
            val = max(0.0, min(1.0, val))
            c = 12.92 * val if val <= 0.0031308 else (1.055 * (val ** (1.0 / 2.4)) - 0.055)
            return int(round(c * 255.0))

        return f"#{gamma(r_lin):02X}{gamma(g_lin):02X}{gamma(b_lin):02X}"

if __name__ == "__main__":
    sim = ThinFilmSimulator(1.00, 1.33, 1.00)
    for d in [10.0, 100.0, 250.0, 380.0, 500.0, 650.0, 1000.0]:
        print(f"Товщина {d:6.1f} нм -> {sim.simulate_hex_color(d)}")
