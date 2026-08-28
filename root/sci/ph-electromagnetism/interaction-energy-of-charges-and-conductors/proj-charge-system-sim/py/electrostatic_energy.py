# electrostatic_energy.py — Векторизований розрахунок мовою Python (NumPy)

import time
import numpy as np

COULOMB_K = 8.9875517923e9  # 1 / (4 * pi * eps0)

def compute_system_energy_numpy(positions: np.ndarray, charges: np.ndarray, r_soft: float = 1e-9) -> float:
    """
    Векторизований розрахунок енергії взаємодії N зарядів у тривимірному просторі.
    positions: масив форми (N, 3) у метрах
    charges:   масив форми (N,) у кулонах
    """
    # Матриця різниць координат: diffs[i, j] = positions[i] - positions[j]
    diffs = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]  # Форма (N, N, 3)
    
    # Квадрати відстаней між усіма парами частинок
    dist_sq = np.sum(diffs ** 2, axis=-1) + r_soft ** 2
    dists = np.sqrt(dist_sq)
    
    # Матриця добутків зарядів: charge_prod[i, j] = charges[i] * charges[j]
    charge_prod = np.outer(charges, charges)
    
    # Обчислюємо верхній трикутник без діагоналі (i < j)
    triu_indices = np.triu_indices(len(charges), k=1)
    
    # Сума енергій попарної взаємодії
    pairwise_energies = (charge_prod[triu_indices] / dists[triu_indices])
    total_energy = COULOMB_K * np.sum(pairwise_energies)
    
    return float(total_energy)

if __name__ == "__main__":
    np.random.seed(12345)
    n_charges = 1000
    
    pos = np.random.rand(n_charges, 3)
    q = np.where(np.arange(n_charges) % 2 == 0, 1e-6, -1e-6)
    
    t0 = time.perf_counter()
    W = compute_system_energy_numpy(pos, q)
    t1 = time.perf_counter()
    
    print(f"Розмір системи: N = {n_charges} зарядів")
    print(f"Повна енергія системи (Python/NumPy): W = {W:.6f} Дж ({W * 1000:.3f} мДж)")
    print(f"Час обчислення (Python/NumPy): {(t1 - t0) * 1000:.3f} мс")
