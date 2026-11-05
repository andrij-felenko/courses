import numpy as np

class IEC60751:
    A = 3.9083e-3
    B = -5.7750e-7
    C = -4.1830e-12

    def __init__(self, r0: float = 100.0):
        self.r0 = r0

    def resistance_to_temperature(self, r: np.ndarray) -> np.ndarray:
        t = np.zeros_like(r, dtype=float)
        
        # Для T >= 0 (R >= R0)
        pos_mask = r >= self.r0
        if np.any(pos_mask):
            r_pos = r[pos_mask]
            t[pos_mask] = (-self.A + np.sqrt(self.A**2 - 4 * self.B * (1.0 - r_pos / self.r0))) / (2 * self.B)
            
        # Для T < 0 (R < R0) використовуємо метод Ньютона
        neg_mask = r < self.r0
        if np.any(neg_mask):
            r_neg = r[neg_mask]
            t_guess = (r_neg / self.r0 - 1) / self.A
            for _ in range(5):
                f = self.r0 * (1 + self.A * t_guess + self.B * t_guess**2 + self.C * (t_guess - 100) * t_guess**3) - r_neg
                df = self.r0 * (self.A + 2 * self.B * t_guess + 4 * self.C * t_guess**3 - 300 * self.C * t_guess**2)
                t_guess -= f / df
            t[neg_mask] = t_guess
            
        return t

    def temperature_to_resistance(self, t: np.ndarray) -> np.ndarray:
        r = np.zeros_like(t, dtype=float)
        
        pos_mask = t >= 0
        if np.any(pos_mask):
            t_pos = t[pos_mask]
            r[pos_mask] = self.r0 * (1 + self.A * t_pos + self.B * t_pos**2)
            
        neg_mask = t < 0
        if np.any(neg_mask):
            t_neg = t[neg_mask]
            r[neg_mask] = self.r0 * (1 + self.A * t_neg + self.B * t_neg**2 + self.C * (t_neg - 100) * t_neg**3)
            
        return r

class LookupTable:
    def __init__(self, t_min: float, t_max: float, step: float, r0: float = 100.0):
        self.sensor = IEC60751(r0)
        self.temperatures = np.arange(t_min, t_max + step, step)
        self.resistances = self.sensor.temperature_to_resistance(self.temperatures)

    def lookup_temperature(self, r: np.ndarray) -> np.ndarray:
        return np.interp(r, self.resistances, self.temperatures)
