import numpy as np
from scipy.optimize import curve_fit

def solve_weiss_magnetization(T, Tc, tol=1e-9, max_iter=500):
    """
    Чисельне розв'язання рівняння Вейсса m = tanh(m * Tc / T) методом простої ітерації.
    """
    T = np.asarray(T, dtype=float)
    m = np.zeros_like(T)
    
    mask_below_tc = T < Tc
    if not np.any(mask_below_tc):
        return m

    T_sub = T[mask_below_tc]
    m_curr = np.full_like(T_sub, 0.99)
    
    for _ in range(max_iter):
        m_next = np.tanh(m_curr * Tc / T_sub)
        if np.max(np.abs(m_next - m_curr)) < tol:
            m_curr = m_next
            break
        m_curr = m_next
        
    m[mask_below_tc] = m_curr
    return m

def curie_weiss_func(T, C, Tc):
    """Модель оберненої магнітної сприйнятливості 1/chi(T)."""
    return (T - Tc) / C

def fit_curie_weiss(T_exp, chi_exp):
    """
    Апроксимація експериментальних даних закону Кюрі — Вейсса МНК.
    """
    inv_chi = 1.0 / chi_exp
    
    p0 = [1.0, 300.0]
    popt, pcov = curve_fit(curie_weiss_func, T_exp, inv_chi, p0=p0)
    
    C_fit, Tc_fit = popt
    C_err, Tc_err = np.sqrt(np.diag(pcov))
    
    k_B = 1.380649e-23
    mu_0 = 4.0 * np.pi * 1e-7
    N_A = 6.02214076e23
    mu_B = 9.27401007e-24
    
    mu_eff_J = np.sqrt((3.0 * k_B * C_fit) / (N_A * mu_0))
    mu_eff_B = mu_eff_J / mu_B
    
    return {
        "C": C_fit, "C_err": C_err,
        "Tc": Tc_fit, "Tc_err": Tc_err,
        "mu_eff_B": mu_eff_B
    }
