def solve_van_der_pauw(R_A, R_B, tol=1e-7):
    """Метод Ньютона-Рафсона для знаходження поверхневого опору R_s."""
    # Початкове наближення за формулою залишку
    R_s = np.pi * (R_A + R_B) / (2.0 * np.log(2.0))
    
    for _ in range(100):
        f = np.exp(-np.pi * R_A / R_s) + np.exp(-np.pi * R_B / R_s) - 1.0
        df = (np.pi * R_A / (R_s**2)) * np.exp(-np.pi * R_A / R_s) + \
             (np.pi * R_B / (R_s**2)) * np.exp(-np.pi * R_B / R_s)
        
        R_s_new = R_s - f / df
        if abs(R_s_new - R_s) < tol:
            return R_s_new
        R_s = R_s_new
    return R_s
