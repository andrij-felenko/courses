import math

class SensoryScaleCalculator:
    def __init__(self, i_zero: float = 1e-5, k_weber: float = 0.01, k_scale: float = 10.0, stevens_n: float = 0.33):
        self.i_zero = i_zero
        self.k_weber = k_weber
        self.k_scale = k_scale
        self.stevens_n = stevens_n

    def calculate_fechner(self, intensity: float) -> float:
        if intensity <= self.i_zero:
            return 0.0
        delta_ratio = (intensity - self.i_zero) / self.i_zero
        return self.k_scale * math.log1p(delta_ratio)

    def calculate_stevens(self, intensity: float) -> float:
        if intensity <= self.i_zero:
            return 0.0
        return self.k_scale * math.pow(intensity - self.i_zero, self.stevens_n)

    def generate_jnd_steps(self, max_intensity: float) -> list[float]:
        if self.k_weber <= 0:
            raise ValueError("Weber fraction must be positive")
        steps = []
        current_i = self.i_zero
        while current_i <= max_intensity:
            steps.append(current_i)
            current_i *= (1.0 + self.k_weber)
        return steps

    @staticmethod
    def linear_to_srgb_8bit(linear_val: float) -> int:
        if linear_val <= 0.0:
            return 0
        if linear_val >= 1.0:
            return 255
        if linear_val <= 0.0031308:
            srgb = 12.92 * linear_val
        else:
            srgb = 1.055 * math.pow(linear_val, 1.0 / 2.4) - 0.055
        return int(min(max(srgb * 255.0 + 0.5, 0.0), 255.0))

if __name__ == "__main__":
    calc = SensoryScaleCalculator(i_zero=1e-5, k_weber=0.01, k_scale=10.0, stevens_n=0.33)
    print("=== Моделювання сенсорних шкал (Python) ===")
    
    test_values = [1e-5, 1e-4, 1e-3, 1e-2, 1.0]
    for val in test_values:
        sf = calc.calculate_fechner(val)
        ss = calc.calculate_stevens(val)
        print(f"I = {val:10.5f} | S_Fechner = {sf:8.4f} | S_Stevens = {ss:8.4f}")

    jnd_steps = calc.generate_jnd_steps(1e-4)
    print(f"Згенеровано {len(jnd_steps)} JND-ступенів")

    print("\nsRGB квантування яскравості:")
    for lum in [0.001, 0.01, 0.1, 0.5, 1.0]:
        px = SensoryScaleCalculator.linear_to_srgb_8bit(lum)
        print(f"Лінійна = {lum:5.3f} -> sRGB 8-bit = {px:3d}")
