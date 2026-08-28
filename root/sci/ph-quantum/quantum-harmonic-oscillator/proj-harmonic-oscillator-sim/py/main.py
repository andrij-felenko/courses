import numpy as np
from scipy.linalg import eigh_tridiagonal

def solve_quantum_harmonic_oscillator(L=5.0, N=1000, num_eigenstates=5):
    """
    Чисельне розв'язання 1D рівняння Шредінгера для гармонічного осцилятора.
    L: межа інтегрування [-L, +L] у безрозмірних одиницях xi = x / x_0
    N: кількість вузлів просторової сітки
    num_eigenstates: кількість перших власних станів для обчислення
    """
    xi = np.linspace(-L, L, N)
    h = xi[1] - xi[0]

    # Діагональні елементи H_ii = 1/h^2 + 0.5 * xi_i^2
    d = 1.0 / (h ** 2) + 0.5 * (xi ** 2)

    # Позадіагональні елементи H_{i, i+1} = -1 / (2 * h^2)
    e = -0.5 / (h ** 2) * np.ones(N - 1)

    # Обчислення власних значень та власних векторів тридіагональної матриці
    eigenvalues, eigenvectors = eigh_tridiagonal(d, e, select='i', select_range=(0, num_eigenstates - 1))

    # Нормування хвильових функцій: int |psi|^2 dxi = 1
    for k in range(num_eigenstates):
        norm = np.sqrt(np.sum(eigenvectors[:, k] ** 2) * h)
        eigenvectors[:, k] /= norm

    return xi, eigenvalues, eigenvectors

if __name__ == "__main__":
    L, N = 5.0, 1000
    xi, energies, psi = solve_quantum_harmonic_oscillator(L=L, N=N, num_eigenstates=5)

    print("Перші 5 обчислених власних значень енергії ε = E / (hbar * w):")
    print("---------------------------------------------------------")
    for n in range(5):
        exact = n + 0.5
        calc = energies[n]
        err = abs(calc - exact)
        print(f"n = {n}: обчислено = {calc:.6f}, точне = {exact:.1f}, похибка = {err:.2e}")
