import cmath
import math

class DrudePlasmonSimulator:
    def __init__(self, wp: float, gamma: float, eps_inf: float = 1.0, eps_d: float = 1.0, n_prism: float = 1.517):
        self.wp = wp
        self.gamma = gamma
        self.eps_inf = eps_inf
        self.eps_d = eps_d
        self.n_prism = n_prism

    def calculate_epsilon(self, omega: float) -> complex:
        if omega <= 0:
            return complex(self.eps_inf, 0.0)
        denom = omega**2 + 1j * self.gamma * omega
        return self.eps_inf - (self.wp**2) / denom

    def calculate_reflectivity(self, eps: complex) -> float:
        n_comp = cmath.sqrt(eps)
        r_amp = (1.0 - n_comp) / (1.0 + n_comp)
        return abs(r_amp)**2

    def calculate_k_spp(self, omega: float, eps_m: complex) -> complex:
        ratio = (eps_m * self.eps_d) / (eps_m + self.eps_d)
        return omega * cmath.sqrt(ratio)

    def calculate_kretschmann_angle(self, k_spp: complex, omega: float) -> float:
        sin_th = k_spp.real / (omega * self.n_prism)
        if sin_th > 1.0 or sin_th < -1.0:
            return 0.0
        return math.asin(sin_th) * (180.0 / math.pi)

    def scan_spectrum(self, start_ev: float, end_ev: float, steps: int):
        results = []
        step_size = (end_ev - start_ev) / (steps - 1)
        for i in range(steps):
            w = start_ev + i * step_size
            eps = self.calculate_epsilon(w)
            n_comp = cmath.sqrt(eps)
            R = self.calculate_reflectivity(eps)
            k_spp = self.calculate_k_spp(w, eps)
            angle = self.calculate_kretschmann_angle(k_spp, w)
            results.append((w, eps.real, eps.imag, n_comp.real, n_comp.imag, R, angle))
        return results

if __name__ == "__main__":
    # Параметри для срібла (Ag)
    sim = DrudePlasmonSimulator(wp=9.01, gamma=0.05, eps_inf=3.7, eps_d=1.0, n_prism=1.517)
    spectrum = sim.scan_spectrum(1.0, 3.5, 10)

    print("===================================================================================")
    print("  w (eV)  |   Re(eps)   |   Im(eps)   |    n    |    k    | Reflectivity R | Angle (deg)")
    print("===================================================================================")
    for w, re_eps, im_eps, n_val, k_val, R, angle in spectrum:
        print(f"  {w:6.3f}  |  {re_eps:9.3f}  |  {im_eps:9.3f}  |  {n_val:6.3f} | {k_val:6.3f} | {R:12.3f}  | {angle:9.3f}")
    print("===================================================================================")
