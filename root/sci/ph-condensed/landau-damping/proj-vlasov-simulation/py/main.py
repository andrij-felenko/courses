import numpy as np

def run_vlasov_landau_simulation(Nx=64, Nv=128, k=0.5, dt=0.1, num_steps=200, alpha=0.05):
    """1D1V Ейлеровий сімулятор рівняння Власова-Пуассона для загасання Ландау."""
    L = 2.0 * np.pi / k
    vmax = 6.0
    dx = L / Nx
    dv = (2.0 * vmax) / Nv

    x = np.linspace(0, L, Nx, endpoint=False)
    v = np.linspace(-vmax + dv/2, vmax - dv/2, Nv)
    X, V = np.meshgrid(x, v, indexing='ij')

    # Початковий максвеллівський розподіл із збуренням густини
    f0 = (1.0 / np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * V**2)
    f = f0 * (1.0 + alpha * np.cos(k * X))

    field_energy = []
    time_points = []

    def solve_poisson(f_dist):
        """Розв'язок рівняння Пуассона через FFT."""
        n_e = np.sum(f_dist, axis=1) * dv
        rho = 1.0 - n_e
        rho_k = np.fft.fft(rho)
        k_vec = 2.0 * np.pi * np.fft.fftfreq(Nx, d=dx)
        k_vec[0] = 1.0  # Уникнення ділення на нуль
        E_k = -1j * rho_k / k_vec
        E_k[0] = 0.0
        return np.real(np.fft.ifft(E_k))

    def shift_x(f_dist, dt_shift):
        """Зсув у просторі x через FFT (спектральний перенос)."""
        f_k = np.fft.fft(f_dist, axis=0)
        k_vec = 2.0 * np.pi * np.fft.fftfreq(Nx, d=dx)[:, np.newaxis]
        f_k_shifted = f_k * np.exp(-1j * k_vec * v[np.newaxis, :] * dt_shift)
        return np.real(np.fft.ifft(f_k_shifted, axis=0))

    def shift_v(f_dist, E_field, dt_shift):
        """Зсув у просторі швидкостей v через FFT."""
        f_k = np.fft.fft(f_dist, axis=1)
        kv_vec = 2.0 * np.pi * np.fft.fftfreq(Nv, d=dv)[np.newaxis, :]
        f_k_shifted = f_k * np.exp(1j * E_field[:, np.newaxis] * kv_vec * dt_shift)
        return np.real(np.fft.ifft(f_k_shifted, axis=1))

    # Головний часовий цикл (сплітінг Ченга — Кнорра)
    for step in range(num_steps):
        t = step * dt
        E = solve_poisson(f)
        E_energy = 0.5 * np.sum(E**2) * dx
        field_energy.append(E_energy)
        time_points.append(t)

        # Сплітінг Strang: dt/2 x -> dt v -> dt/2 x
        f = shift_x(f, 0.5 * dt)
        E = solve_poisson(f)
        f = shift_v(f, E, dt)
        f = shift_x(f, 0.5 * dt)

    return np.array(time_points), np.array(field_energy)

if __name__ == "__main__":
    t, W_E = run_vlasov_landau_simulation(k=0.5, num_steps=150)
    print(f"Початкова енергія полях W_E(0) = {W_E[0]:.6e}")
    print(f"Енергія поля при t={t[-1]:.1f}: W_E(t) = {W_E[-1]:.6e}")
    # Обчислення чисельного декременту з логарифмічного нахилу ln(W_E) = -2|γ|t
    log_W = np.log(W_E[10:60])
    poly = np.polyfit(t[10:60], log_W, 1)
    gamma_num = -poly[0] / 2.0
    print(f"Чисельно виміряний декремент загасання γ_num = {gamma_num:.4f}")
    print("Теоретичний декремент Ландау для k=0.5: γ_th = 0.1533")
