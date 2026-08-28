import numpy as np
from scipy.optimize import curve_fit

def debye_real(f, eps_s, eps_inf, tau):
    """Модель Дебая для дійсної частини проникності ε'(f)"""
    omega = 2.0 * np.pi * f
    return eps_inf + (eps_s - eps_inf) / (1.0 + (omega * tau)**2)

def debye_imag(f, eps_s, eps_inf, tau):
    """Модель Дебая для уявної частини проникності ε''(f)"""
    omega = 2.0 * np.pi * f
    return (eps_s - eps_inf) * (omega * tau) / (1.0 + (omega * tau)**2)

def fit_dielectric_spectrum(freq_data_hz, eps_real_data, eps_imag_data):
    """
    Нелінійний МНК-аналіз кривих проникності для визначення часу релаксації τ
    """
    p0 = [80.0, 4.5, 1e-9]
    bounds = ([1.0, 1.0, 1e-13], [300.0, 50.0, 1e-3])

    popt_real, _ = curve_fit(debye_real, freq_data_hz, eps_real_data, p0=p0, bounds=bounds)
    eps_s_fit, eps_inf_fit, tau_fit = popt_real

    f_max_loss = 1.0 / (2.0 * np.pi * tau_fit)
    
    print(f"--- Результати апроксимації релаксації Дебая ---")
    print(f"Статична проникність ε_s:      {eps_s_fit:.2f}")
    print(f"Високочастотна проникність ε_∞: {eps_inf_fit:.2f}")
    print(f"Час релаксації τ:               {tau_fit*1e12:.2f} пс")
    print(f"Частота максимуму втрат f_max:  {f_max_loss/1e9:.3f} ГГц")

    return eps_s_fit, eps_inf_fit, tau_fit

# Симуляція експериментальних даних для полярного розчинника
freqs = np.logspace(6, 11, 200) # 1 МГц - 100 ГГц
true_eps_s, true_eps_inf, true_tau = 78.4, 4.2, 8.2e-11 # Дистильована вода при 25 °C

noisy_eps_re = debye_real(freqs, true_eps_s, true_eps_inf, true_tau) + np.random.normal(0, 0.3, len(freqs))
noisy_eps_im = debye_imag(freqs, true_eps_s, true_eps_inf, true_tau) + np.random.normal(0, 0.2, len(freqs))

fit_dielectric_spectrum(freqs, noisy_eps_re, noisy_eps_im)
