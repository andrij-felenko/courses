import math

class DoubleSlitSimulator:
    def __init__(self, wavelength: float = 632.8e-9, d: float = 0.2e-3, 
                 a: float = 0.04e-3, L: float = 2.0, gamma: float = 1.0):
        self.wavelength = wavelength
        self.d = d
        self.a = a
        self.L = L
        self.gamma = gamma

    def intensity(self, y: float) -> float:
        if self.L <= 0.0 or self.wavelength <= 0.0:
            return 0.0

        sin_theta = y / math.sqrt(y**2 + self.L**2)
        alpha = (math.pi * self.d * sin_theta) / self.wavelength
        beta = (math.pi * self.a * sin_theta) / self.wavelength

        interference = 1.0 + self.gamma * math.cos(2.0 * alpha)

        if abs(beta) > 1e-7:
            sinc = math.sin(beta) / beta
            diffraction = sinc**2
        else:
            diffraction = 1.0 - (beta**2) / 3.0

        return interference * diffraction

    def generate_profile(self, y_max: float, steps: int) -> list[tuple[float, float]]:
        dy = (2.0 * y_max) / (steps - 1)
        return [(-y_max + i * dy, self.intensity(-y_max + i * dy)) for i in range(steps)]

    def render_ascii(self, y_max: float, steps: int, max_bars: int = 40) -> None:
        print("=== Двощілинна інтерференція (Python) ===")
        print(f"Параметри: λ = {self.wavelength*1e9:.1f} нм, d = {self.d*1e3:.2f} мм, "
              f"a = {self.a*1e3:.2f} мм, L = {self.L:.1f} м, γ = {self.gamma:.2f}\n")

        dy = (2.0 * y_max) / (steps - 1)
        for i in range(steps):
            y = -y_max + i * dy
            val = self.intensity(y)
            stars = int(val * (max_bars / 2.0))
            print(f"{y*1e3:+6.2f} мм | {'*' * stars} ({val:.3f})")

if __name__ == '__main__':
    sim = DoubleSlitSimulator()
    sim.render_ascii(y_max=0.015, steps=21, max_bars=40)
