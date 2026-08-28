import numpy as np

class RamseyPhysics:
    """Фізична модель спектра Рамзі з урахуванням атомного дробового шуму."""
    def __init__(self, tau=0.010, T=0.500, n_atoms=1_000_000, seed=42):
        self.tau = tau
        self.T = T
        self.n_atoms = n_atoms
        self.rng = np.random.default_rng(seed)
        self.cs_freq = 9_192_631_770.0

    def compute_probability(self, detuning_hz):
        delta = 2.0 * np.pi * detuning_hz
        omega_rabi = np.pi / (2.0 * self.tau)
        omega_eff = np.sqrt(omega_rabi**2 + delta**2)

        sin_pulse = np.sin(omega_eff * self.tau / 2.0)
        cos_pulse = np.cos(omega_eff * self.tau / 2.0)

        term1 = cos_pulse * np.cos(delta * self.T / 2.0)
        term2 = (delta / omega_eff) * sin_pulse * np.sin(delta * self.T / 2.0)

        p_rabi = 4.0 * (omega_rabi**2 / omega_eff**2) * (sin_pulse**2)
        p_ramsey = p_rabi * ((term1 - term2)**2)
        return np.clip(p_ramsey, 0.0, 1.0)

    def measure_fraction(self, detuning_hz):
        p_true = self.compute_probability(detuning_hz)
        std_dev = np.sqrt(p_true * (1.0 - p_true) / self.n_atoms)
        noise = self.rng.normal(0.0, std_dev)
        return np.clip(p_true + noise, 0.0, 1.0)

class FrequencyServoPID:
    """Цифровий PID-регулятор частоти."""
    def __init__(self, Kp=0.4, Ki=0.1, Kd=0.01):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, error, dt=1.0):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative

def compute_allan_deviation(y_series, dt=1.0):
    """Обчислення двовибіркової девіації Аллана sigma_y(tau)."""
    N = len(y_series)
    max_m = N // 4
    m_values = [2**i for i in range(int(np.log2(max_m)) + 1)]
    results = []

    for m in m_values:
        tau = m * dt
        K = N // m
        bar_y = np.mean(y_series[:K*m].reshape(K, m), axis=1)
        diffs = np.diff(bar_y)
        sigma_sq = np.sum(diffs**2) / (2.0 * (K - 1))
        results.append((tau, np.sqrt(sigma_sq)))

    return results

if __name__ == "__main__":
    physics = RamseyPhysics(tau=0.010, T=0.500, n_atoms=1_000_000)
    pid = FrequencyServoPID()

    f0 = physics.cs_freq
    vcxo_freq = f0 + 0.15  # Початкова помилка +0.15 Гц
    mod_offset = 1.0 / (4.0 * physics.T) # +/- 0.5 Гц модуляція

    history_y = []
    total_steps = 1000

    for step in range(total_steps):
        # Модуляційне вимірювання лівого та правого схилів
        p_left = physics.measure_fraction(vcxo_freq - f0 - mod_offset)
        p_right = physics.measure_fraction(vcxo_freq - f0 + mod_offset)

        # Сигнал дискримінатора
        error_signal = p_right - p_left

        # PID корекція
        correction = pid.update(error_signal, dt=1.0)
        vcxo_freq -= correction

        y_val = (vcxo_freq - f0) / f0
        history_y.append(y_val)

    # Статистика Аллана
    adev_data = compute_allan_deviation(np.array(history_y), dt=1.0)
    print("Результати моделювання (tau -> sigma_y):")
    for tau, adev in adev_data:
        print(f"tau = {tau:4.0f} s | sigma_y(tau) = {adev:.3e}")
