def build_delay_matrix(signal: np.ndarray, m: int, delay: int) -> np.ndarray:
    """
    Формування затримкової матриці Y розміром (N_eff, m).
    """
    n_eff = len(signal) - (m - 1) * delay
    if n_eff <= 0:
        raise ValueError("Занадто великі m або delay для даної довжини сигналу")
        
    matrix = np.zeros((n_eff, m))
    for j in range(m):
        matrix[:, j] = signal[j * delay : j * delay + n_eff]
    return matrix
