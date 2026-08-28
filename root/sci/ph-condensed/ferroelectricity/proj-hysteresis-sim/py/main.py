import math
from typing import List, Tuple

class FerroelectricSimulation:
    def __init__(self, alpha: float = -1.0, beta: float = 1.0, 
                 gamma: float = 0.1, e_amp: float = 1.5, 
                 freq: float = 1.0, e_bias: float = 0.0):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.e_amp = e_amp
        self.freq = freq
        self.e_bias = e_bias

    def derivative(self, t: float, p: float) -> float:
        e_field = self.e_amp * math.sin(2.0 * math.pi * self.freq * t) + self.e_bias
        df_dp = self.alpha * p + self.beta * (p ** 3) - e_field
        return -df_dp / self.gamma

    def step_rk4(self, t: float, p: float, dt: float) -> float:
        k1 = self.derivative(t, p)
        k2 = self.derivative(t + 0.5 * dt, p + 0.5 * dt * k1)
        k3 = self.derivative(t + 0.5 * dt, p + 0.5 * dt * k2)
        k4 = self.derivative(t + dt, p + dt * k3)
        return p + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    def run(self, dt: float = 0.0005, steps: int = 4000) -> Tuple[List[Tuple[float, float, float]], float]:
        t, p = 0.0, 0.1
        history = []
        energy_loss = 0.0
        prev_e, prev_p = 0.0, 0.1
        
        for i in range(steps):
            e_field = self.e_amp * math.sin(2.0 * math.pi * self.freq * t) + self.e_bias
            if i >= steps // 2:
                history.append((t, e_field, p))
                dp = p - prev_p
                avg_e = 0.5 * (e_field + prev_e)
                energy_loss += avg_e * dp
            prev_e, prev_p = e_field, p
            p = self.step_rk4(t, p, dt)
            t += dt
        return history, energy_loss

if __name__ == "__main__":
    sim = FerroelectricSimulation()
    results, loss = sim.run()
    print(f"Симуляція успішна: отримано {len(results)} точок.")
    print(f"Обчислено енергетичні втрати за цикл W = {loss:.4f} у.о.")
