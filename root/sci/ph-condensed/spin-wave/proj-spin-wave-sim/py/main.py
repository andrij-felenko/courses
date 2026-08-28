import numpy as np

def simulate_spin_wave_dispersion(N=256, steps=1024, dt=0.02, J=1.0, B0=0.2, alpha=0.005):
    """
    Моделювання спінового ланцюжка та розрахунок дисперсії w(k) через 2D FFT
    """
    spins = np.zeros((N, 3))
    spins[:, 2] = 1.0  # Основний стан (всі спини уздовж Z)

    # Дельта-імпульсне збудження широкого спектра у центрі ланцюжка
    spins[N // 2, 0] += 0.3
    spins[N // 2] /= np.linalg.norm(spins[N // 2])

    sx_history = np.zeros((steps, N))

    gamma_prime = 1.0 / (1.0 + alpha**2)

    def llg_rhs(state):
        rhs = np.zeros_like(state)
        # Сусідні спіни з періодичними граничними умовами
        s_prev = np.roll(state, 1, axis=0)
        s_next = np.roll(state, -1, axis=0)

        b_eff = np.zeros_like(state)
        b_eff[:, 0] = J * (s_prev[:, 0] + s_next[:, 0])
        b_eff[:, 1] = J * (s_prev[:, 1] + s_next[:, 1])
        b_eff[:, 2] = B0 + J * (s_prev[:, 2] + s_next[:, 2])

        prec = np.cross(state, b_eff)
        damp = np.cross(state, prec)
        
        return -gamma_prime * prec - (alpha * gamma_prime) * damp

    # Часова інтеграція RK4
    for t in range(steps):
        sx_history[t, :] = spins[:, 0]

        k1 = llg_rhs(spins)
        k2 = llg_rhs(spins + 0.5 * dt * k1)
        k3 = llg_rhs(spins + 0.5 * dt * k2)
        k4 = llg_rhs(spins + dt * k3)

        spins += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        
        # Ренормування спинових векторів
        norms = np.linalg.norm(spins, axis=1, keepdims=True)
        spins /= norms

    # 2D FFT для отримання карти дисперсії I(k, w)
    fft_spectrum = np.abs(np.fft.fft2(sx_history))
    fft_shifted = np.fft.fftshift(fft_spectrum)

    print(f"Симуляцію завершено. Форма матриці дисперсії: {fft_shifted.shape}")
    print(f"Максимум спектрального відгуку: {np.max(fft_shifted):.2f}")

    return sx_history, fft_shifted

if __name__ == "__main__":
    history, spectrum = simulate_spin_wave_dispersion()
