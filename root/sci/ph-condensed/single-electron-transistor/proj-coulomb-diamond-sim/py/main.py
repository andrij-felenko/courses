import numpy as np
import math

class SETSimulator:
    """
    Симулятор одноелектронного транзистора (SET) на основі ортодоксальної теорії.
    """
    def __init__(self, C1=1e-18, C2=1e-18, Cg=2e-18, R1=100e3, R2=100e3, Temp=0.5):
        self.C1 = C1
        self.C2 = C2
        self.Cg = Cg
        self.C_total = C1 + C2 + Cg
        self.R1 = R1
        self.R2 = R2
        self.Temp = Temp
        self.e = 1.602176634e-19
        self.kB = 1.380649e-23
        self.Ec = (self.e ** 2) / (2.0 * self.C_total)

    def _rate(self, delta_F, R_tunnel):
        """Обчислення швидкості тунелювання за теорією Фермі."""
        if abs(delta_F) < 1e-30:
            return (self.kB * self.Temp) / (self.e ** 2 * R_tunnel)
        
        arg = delta_F / (self.kB * self.Temp)
        if arg > 100.0:
            return 0.0
        elif arg < -100.0:
            return -delta_F / (self.e ** 2 * R_tunnel)
        else:
            return delta_F / (self.e ** 2 * R_tunnel * (1.0 - math.exp(-arg)))

    def calculate_current(self, Vds, Vg, n_max=10):
        """Розрахунок струму I_ds при заданих напругах Vds та Vg."""
        n_values = np.arange(-n_max, n_max + 1)
        num_states = len(n_values)
        
        gamma_1_plus = np.zeros(num_states)
        gamma_1_minus = np.zeros(num_states)
        gamma_2_plus = np.zeros(num_states)
        gamma_2_minus = np.zeros(num_states)

        Vs = Vds / 2.0
        Vd = -Vds / 2.0

        for idx, n in enumerate(n_values):
            # Перехід n -> n + 1 через Перехід 1 (Source)
            dF_1_plus = self.Ec * (1.0 + 2.0 * (n - (self.Cg * Vg + self.C1 * Vs + self.C2 * Vd) / self.e)) - self.e * Vs
            gamma_1_plus[idx] = self._rate(dF_1_plus, self.R1)

            # Перехід n -> n - 1 через Перехід 1 (Source)
            dF_1_minus = self.Ec * (1.0 - 2.0 * (n - (self.Cg * Vg + self.C1 * Vs + self.C2 * Vd) / self.e)) + self.e * Vs
            gamma_1_minus[idx] = self._rate(dF_1_minus, self.R1)

            # Перехід n -> n + 1 через Перехід 2 (Drain)
            dF_2_plus = self.Ec * (1.0 + 2.0 * (n - (self.Cg * Vg + self.C1 * Vs + self.C2 * Vd) / self.e)) - self.e * Vd
            gamma_2_plus[idx] = self._rate(dF_2_plus, self.R2)

            # Перехід n -> n - 1 через Перехід 2 (Drain)
            dF_2_minus = self.Ec * (1.0 - 2.0 * (n - (self.Cg * Vg + self.C1 * Vs + self.C2 * Vd) / self.e)) + self.e * Vd
            gamma_2_minus[idx] = self._rate(dF_2_minus, self.R2)

        # Розв'язок стаціонарного рівняння балансу
        P = np.zeros(num_states)
        P[n_max] = 1.0  # початкове значення для n=0

        # Прямий хід для n > 0
        for i in range(n_max, num_states - 1):
            W_plus = gamma_1_plus[i] + gamma_2_plus[i]
            W_minus = gamma_1_minus[i + 1] + gamma_2_minus[i + 1]
            if W_minus > 0:
                P[i + 1] = P[i] * (W_plus / W_minus)

        # Зворотний хід для n < 0
        for i in range(n_max, 0, -1):
            W_minus = gamma_1_minus[i] + gamma_2_minus[i]
            W_plus = gamma_1_plus[i - 1] + gamma_2_plus[i - 1]
            if W_plus > 0:
                P[i - 1] = P[i] * (W_minus / W_plus)

        # Нормування ймовірностей
        sum_P = np.sum(P)
        if sum_P > 0:
            P /= sum_P

        # Обчислення результуючого струму
        I_ds = self.e * np.sum(P * (gamma_1_plus - gamma_1_minus))
        return I_ds

    def simulate_coulomb_diamonds(self, Vg_vec, Vds_vec):
        """Генерація 2D матриці струму для графіку ромбів Кулона."""
        I_matrix = np.zeros((len(Vds_vec), len(Vg_vec)))
        for i, Vds in enumerate(Vds_vec):
            for j, Vg in enumerate(Vg_vec):
                I_matrix[i, j] = self.calculate_current(Vds, Vg)
        return I_matrix

if __name__ == "__main__":
    sim = SETSimulator(Temp=0.1)
    Vg_vec = np.linspace(-0.1, 0.1, 100)
    Vds_vec = np.linspace(-0.05, 0.05, 100)
    I_map = sim.simulate_coulomb_diamonds(Vg_vec, Vds_vec)
    print(f"Розраховано карту {I_map.shape}, макс струм: {np.max(np.abs(I_map))*1e9:.3f} нА")
