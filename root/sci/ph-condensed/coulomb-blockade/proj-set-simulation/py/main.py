import math
import numpy as np

class SingleElectronTransistor:
    """Модель одноелектронного транзистора (SET) за ортодоксальною теорією."""
    
    def __init__(self, C_s=1.0e-18, C_d=1.0e-18, C_g=0.5e-18, 
                 R_s=100.0e3, R_d=100.0e3, T=0.1):
        self.e = 1.602176634e-19
        self.k_B = 1.380649e-23
        self.C_s = C_s
        self.C_d = C_d
        self.C_g = C_g
        self.C_sum = C_s + C_d + C_g
        self.R_s = R_s
        self.R_d = R_d
        self.T = T
        self.E_c = (self.e ** 2) / (2.0 * self.C_sum)

    def rate(self, delta_E, R_T):
        """Розрахунок швидкості тунелювання за Золотим правилом Фермі."""
        if self.T < 1.0e-6:
            return -delta_E / ((self.e ** 2) * R_T) if delta_E < 0.0 else 0.0
        
        x = delta_E / (self.k_B * self.T)
        if x > 100.0:
            return 0.0
        elif x < -100.0:
            return -delta_E / ((self.e ** 2) * R_T)
        elif abs(x) < 1.0e-6:
            return (self.k_B * self.T) / ((self.e ** 2) * R_T)
        else:
            return -delta_E / (((self.e ** 2) * R_T) * (1.0 - math.exp(x)))

    def calculate_current(self, V_ds, V_g, N_max=10):
        """Обчислення тунельного струму I(V_ds, V_g)."""
        states = np.arange(-N_max, N_max + 1)
        dim = len(states)
        n_g = (self.C_g * V_g) / self.e

        gamma_s_plus = np.zeros(dim)
        gamma_s_minus = np.zeros(dim)
        gamma_d_plus = np.zeros(dim)
        gamma_d_minus = np.zeros(dim)

        for i, n in enumerate(states):
            # ΔE_s+ (n -> n+1 from Source)
            dE_sp = self.E_c * (1.0 + 2.0 * (n - n_g)) - self.e * V_ds * (self.C_d + self.C_g / 2.0) / self.C_sum
            gamma_s_plus[i] = self.rate(dE_sp, self.R_s)

            # ΔE_s- (n -> n-1 to Source)
            dE_sm = self.E_c * (1.0 - 2.0 * (n - n_g)) + self.e * V_ds * (self.C_d + self.C_g / 2.0) / self.C_sum
            gamma_s_minus[i] = self.rate(dE_sm, self.R_s)

            # ΔE_d+ (n -> n+1 from Drain)
            dE_dp = self.E_c * (1.0 + 2.0 * (n - n_g)) + self.e * V_ds * (self.C_s + self.C_g / 2.0) / self.C_sum
            gamma_d_plus[i] = self.rate(dE_dp, self.R_d)

            # ΔE_d- (n -> n-1 to Drain)
            dE_dm = self.E_c * (1.0 - 2.0 * (n - n_g)) - self.e * V_ds * (self.C_s + self.C_g / 2.0) / self.C_sum
            gamma_d_minus[i] = self.rate(dE_dm, self.R_d)

        # Побудова співвідношень P(n+1)/P(n)
        ratio = np.zeros(dim - 1)
        for i in range(dim - 1):
            denom = gamma_s_minus[i + 1] + gamma_d_minus[i + 1]
            num = gamma_s_plus[i] + gamma_d_plus[i]
            ratio[i] = num / denom if denom > 0.0 else 0.0

        # Нормування ймовірностей P(n)
        P = np.zeros(dim)
        P[0] = 1.0
        for i in range(1, dim):
            P[i] = P[i - 1] * ratio[i - 1]
        
        p_sum = np.sum(P)
        if p_sum > 0.0:
            P /= p_sum

        # Струм через витоковий контакт
        current = 0.0
        for i in range(dim):
            current += P[i] * (gamma_s_plus[i] - gamma_s_minus[i])
        
        return self.e * current

def simulate_coulomb_diamonds(set_dev, v_g_vec, v_ds_vec):
    """Генерація 2D карти струму у координатах (V_g, V_ds)."""
    grid = np.zeros((len(v_ds_vec), len(v_g_vec)))
    for j, v_ds in enumerate(v_ds_vec):
        for i, v_g in enumerate(v_g_vec):
            grid[j, i] = set_dev.calculate_current(v_ds, v_g)
    return grid

if __name__ == "__main__":
    set_sim = SingleElectronTransistor(T=0.05)
    I_val = set_sim.calculate_current(V_ds=0.001, V_g=0.002)
    print(f"Струм SET при V_ds=1 мВ, V_g=2 мВ: {I_val * 1e9:.3f} нА")
