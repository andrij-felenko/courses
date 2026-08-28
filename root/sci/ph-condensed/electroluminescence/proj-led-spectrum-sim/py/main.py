import math
import numpy as np

class LedSimulator:
    def __init__(self, bandgap_ev=1.42, temp_k=300.0, active_layer_nm=10.0,
                 coeff_a=1.0e7, coeff_b=1.0e-10, coeff_c=1.0e-30):
        self.eg = bandgap_ev
        self.temp_k = temp_k
        self.d_cm = active_layer_nm * 1e-7
        self.a = coeff_a
        self.b = coeff_b
        self.c = coeff_c
        
        self.kb_ev = 8.617333262145e-5
        self.hc_ev_nm = 1239.84193
        self.q = 1.602176634e-19

    def calculate_spectrum(self, min_ev=1.35, max_ev=1.60, points=100):
        energies = np.linspace(min_ev, max_ev, points)
        kt = self.kb_ev * self.temp_k
        
        intensities = np.zeros_like(energies)
        mask = energies >= self.eg
        delta_e = energies[mask] - self.eg
        
        intensities[mask] = (energies[mask]**2) * np.sqrt(delta_e) * np.exp(-delta_e / kt)
        
        if np.max(intensities) > 0:
            intensities /= np.max(intensities)
            
        wavelengths = self.hc_ev_nm / energies
        return list(zip(energies, wavelengths, intensities))

    def calculate_efficiency_curve(self, min_log_n=15.0, max_log_n=19.0, points=50):
        log_n = np.linspace(min_log_n, max_log_n, points)
        n = 10.0**log_n
        
        r_srh = self.a * n
        r_rad = self.b * (n**2)
        r_auger = self.c * (n**3)
        r_total = r_srh + r_rad + r_auger
        
        j_a_cm2 = self.q * self.d_cm * r_total
        eta_int = (r_rad / r_total) * 100.0
        
        return list(zip(j_a_cm2, n, eta_int))

if __name__ == '__main__':
    sim = LedSimulator(bandgap_ev=1.42, temp_k=300.0)
    
    spectrum = sim.calculate_spectrum(min_ev=1.35, max_ev=1.60, points=10)
    print("=== Спектр (Python) ===")
    for e, wl, I in spectrum:
        print(f"E = {e:.3f} eV, λ = {wl:.1f} nm, I = {I:.3f}")
        
    eff = sim.calculate_efficiency_curve(min_log_n=15.0, max_log_n=19.0, points=5)
    print("\n=== Ефективність (Python) ===")
    for j, n, eta in eff:
        print(f"J = {j:.2e} A/cm², n = {n:.2e} cm⁻³, η_int = {eta:.1f}%")
