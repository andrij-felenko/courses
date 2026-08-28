import numpy as np

class FDTToolkit:
    """
    Python-аналог бібліотеки FDT Toolkit для наукових обчислень.
    """
    def __init__(self, temperature=300.0):
        self.T = temperature
        self.kB = 1.380649e-23
        self.hbar = 1.054571817e-34

    def callen_welton_factor(self, omega):
        """Обчислення фактора coth(hbar * omega / (2 * kB * T))"""
        if abs(omega) < 1e-12:
            return (2.0 * self.kB * self.T) / (self.hbar * 1e-12)
        x = (self.hbar * abs(omega)) / (2.0 * self.kB * self.T)
        if x < 1e-4:
            return 1.0 / x # Класична границя
        return 1.0 / np.tanh(x)

    def theoretical_psd(self, omegas, im_chi):
        """Розрахунок теоретичної спектральної густини флуктуацій за ТФД"""
        factors = np.array([self.callen_welton_factor(w) for w in omegas])
        return self.hbar * factors * im_chi
