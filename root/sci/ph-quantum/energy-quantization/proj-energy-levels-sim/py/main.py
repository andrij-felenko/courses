import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh

def solve_schrodinger_grid(v_func, z_min=-6.0, z_max=6.0, N=1200, num_levels=5):
    """
    Чисельне знаходження власних значень та хвильових функцій рівняння Шредінгера
    за допомогою сіткового методу скінченних різниць.
    """
    z = np.linspace(z_min, z_max, N)
    h = z[1] - z[0]
    
    # Побудова тридіагональних діагоналей матриці Гамільтоніана H
    diag_main = 1.0 / (h**2) + v_func(z[1:-1])
    diag_off = -0.5 / (h**2) * np.ones(N - 3)
    
    # Збирання розрідженої тридіагональної матриці
    H_matrix = diags([diag_off, diag_main, diag_off], [-1, 0, 1], format='csr')
    
    # Пошук найменших власних значень (SA = Smallest Algebraic)
    energies, wavefunctions = eigsh(H_matrix, k=num_levels, which='SA')
    
    # Додавання нульових крайових умов та чисельне нормування хвильових функцій
    normalized_wfs = []
    for idx in range(num_levels):
        wf = np.pad(wavefunctions[:, idx], (1, 1), mode='constant')
        norm = np.sqrt(np.trapz(wf**2, z))
        normalized_wfs.append(wf / norm)
        
    return z, energies, normalized_wfs

# Потенціал ангармонічного осцилятора
v_anharmonic = lambda z: 0.5 * z**2 + 0.1 * z**4

z_grid, E_vals, psi_funcs = solve_schrodinger_grid(v_anharmonic, z_min=-6.0, z_max=6.0, N=1200, num_levels=5)

print("=== Рівні енергії ангармонічного осцилятора (Python Grid Method) ===")
for n, E in enumerate(E_vals):
    print(f"Рівень n={n}: E_{n} = {E:.6f}")
