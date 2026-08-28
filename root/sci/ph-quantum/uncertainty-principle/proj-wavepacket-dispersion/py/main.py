# py
import numpy as np

def simulate_wavepacket(N=400, x_min=-20.0, x_max=20.0, dt=0.01, steps=200, sigma0=1.0, k0=2.0):
    x = np.linspace(x_min, x_max, N)
    dx = x[1] - x[0]

    # Початковий Гаусів пакет
    psi = (1.0 / (2.0 * np.pi * sigma0**2)**0.25) * np.exp(-x**2 / (4.0 * sigma0**2) + 1j * k0 * x)

    # Параметри Кранка - Ніколсон
    alpha = dt / (4.0 * dx**2)
    diag_main = (1.0 + 2j * alpha) * np.ones(N, dtype=complex)
    diag_off = (-1j * alpha) * np.ones(N - 1, dtype=complex)

    # Побудова тридіагональної матриці
    A = np.diag(diag_main) + np.diag(diag_off, k=1) + np.diag(diag_off, k=-1)

    print("Крок\tНорма\t\tСереднє X\tШирина sigma(t)")
    for step in range(steps + 1):
        norm = np.sum(np.abs(psi)**2) * dx
        mean_x = np.sum(x * np.abs(psi)**2) * dx / norm
        sigma_x = np.sqrt(np.sum((x - mean_x)**2 * np.abs(psi)**2) * dx / norm)

        if step % 40 == 0:
            print(f"{step}\t{norm:.5f}\t{mean_x:.4f}\t\t{sigma_x:.4f}")

        # Формування правої частини
        rhs = np.zeros_like(psi)
        rhs[1:-1] = (1.0 - 2j * alpha) * psi[1:-1] + 1j * alpha * (psi[:-2] + psi[2:])

        # Розв'язання СЛАУ
        psi = np.linalg.solve(A, rhs)

if __name__ == "__main__":
    simulate_wavepacket()
