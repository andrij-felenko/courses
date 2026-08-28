import math
import random
import numpy as np


class LandauPotential:
    """Обчислювач термодинамічного потенціалу Ландау."""

    def __init__(self, a0: float, b: float, Tc: float):
        self.a0 = a0
        self.b = b
        self.Tc = Tc

    def energy(self, T: float, eta: float, H: float = 0.0) -> float:
        a = self.a0 * (T - self.Tc)
        return a * eta**2 + 0.5 * self.b * eta**4 - eta * H

    def find_equilibrium_eta(
        self, T: float, H: float = 0.0, eta_init: float = 0.8
    ) -> float:
        if T >= self.Tc and abs(H) < 1e-9:
            return 0.0

        eta = (
            math.sqrt(self.a0 * (self.Tc - T) / self.b)
            if (T < self.Tc and eta_init == 0.0)
            else eta_init
        )
        a = self.a0 * (T - self.Tc)

        for _ in range(100):
            grad = 2.0 * a * eta + 2.0 * self.b * eta**3 - H
            hessian = 2.0 * a + 6.0 * self.b * eta**2
            if abs(hessian) < 1e-12:
                break
            step = grad / hessian
            eta -= step
            if abs(step) < 1e-9:
                break
        return eta

    def heat_capacity(self, T: float, C0: float = 1.0) -> float:
        return C0 if T >= self.Tc else C0 + (self.a0**2 * T) / self.b


class IsingModel2D:
    """Монте-Карло симулятор 2D моделі Ізинґа (алгоритм Метрополіса)."""

    def __init__(self, L: int, J: float = 1.0, seed: int = 42):
        self.L = L
        self.J = J
        np.random.seed(seed)
        random.seed(seed)
        self.spins = np.ones((L, L), dtype=int)

    def sweep(self, T: float, H: float = 0.0):
        beta = 1.0 / T
        for _ in range(self.L * self.L):
            x = random.randint(0, self.L - 1)
            y = random.randint(0, self.L - 1)
            s = self.spins[y, x]

            neighbors = (
                self.spins[(y + 1) % self.L, x]
                + self.spins[(y - 1) % self.L, x]
                + self.spins[y, (x + 1) % self.L]
                + self.spins[y, (x - 1) % self.L]
            )

            dE = 2.0 * s * (self.J * neighbors + H)
            if dE <= 0.0 or random.random() < math.exp(-dE * beta):
                self.spins[y, x] = -s

    def magnetization(self) -> float:
        return abs(np.sum(self.spins)) / (self.L * self.L)


if __name__ == "__main__":
    Tc_exact = 2.269
    landau = LandauPotential(a0=1.0, b=1.0, Tc=Tc_exact)

    print("=== 1. Мінімізація потенціалу Ландау ===")
    print("T/Tc\t\tT [K]\t\teta (Ландау)\tCp")
    print("-" * 48)
    for rel_T in np.arange(0.5, 1.5, 0.1):
        T = rel_T * landau.Tc
        eta = landau.find_equilibrium_eta(T)
        Cp = landau.heat_capacity(T)
        print(f"{rel_T:.1f}\t\t{T:.3f}\t\t{eta:.4f}\t\t{Cp:.4f}")

    print("\n=== 2. Монте-Карло симуляція 2D Ізинґа (L=32) ===")
    ising = IsingModel2D(L=32, J=1.0)
    print("T/Tc\t\tT [J/kB]\t|M| (Monte-Carlo)")
    print("-" * 48)

    for rel_T in [0.6, 0.8, 0.95, 1.0, 1.05, 1.2, 1.4]:
        T = rel_T * Tc_exact
        for _ in range(1000):
            ising.sweep(T)

        m_acc = 0.0
        for _ in range(1000):
            ising.sweep(T)
            m_acc += ising.magnetization()
        m_avg = m_acc / 1000.0
        print(f"{rel_T:.2f}\t\t{T:.3f}\t\t{m_avg:.4f}")
