import numpy as np

def generate_spectrum(wavelength_center_nm, fwhm_nm, num_points=2048, profile='gaussian'):
    """
    Генерує масив спектральної густини потужності S(nu) для заданої довжини хвилі та ширини лінії.
    """
    c = 299792458.0  # швидкість світла в м/с
    lambda0 = wavelength_center_nm * 1e-9
    delta_lambda = fwhm_nm * 1e-9
    
    nu0 = c / lambda0
    delta_nu = (c / (lambda0 ** 2)) * delta_lambda
    
    # Частотний інтервал навколо центральної частоти nu0
    nu_vector = np.linspace(nu0 - 5 * delta_nu, nu0 + 5 * delta_nu, num_points)
    
    if profile == 'gaussian':
        sigma_nu = delta_nu / (2 * np.sqrt(2 * np.log(2)))
        spectrum = np.exp(-0.5 * ((nu_vector - nu0) / sigma_nu) ** 2)
    elif profile == 'lorentzian':
        spectrum = 1.0 / (1.0 + 4.0 * ((nu_vector - nu0) / delta_nu) ** 2)
    else:
        raise ValueError("Невідомий тип профілю. Обирайте 'gaussian' або 'lorentzian'")
        
    # Нормування спектра
    spectrum /= np.trapz(spectrum, nu_vector)
    return nu_vector, spectrum

def compute_interferogram(nu_vector, spectrum, max_delay_fs=500, steps=1000):
    """
    Обчислює інтерферограму Майкельсона та комплексний ступень когерентності gamma(tau).
    """
    c = 299792458.0
    tau_vector = np.linspace(-max_delay_fs * 1e-15, max_delay_fs * 1e-15, steps)
    dnu = nu_vector[1] - nu_vector[0]
    
    gamma_complex = np.zeros(len(tau_vector), dtype=complex)
    
    # Дискретне інтегрування: gamma(tau) = int S(nu) * exp(i * 2*pi * nu * tau) dnu
    for i, tau in enumerate(tau_vector):
        integrand = spectrum * np.exp(1j * 2 * np.pi * nu_vector * tau)
        gamma_complex[i] = np.trapz(integrand, nu_vector)
        
    # Нормування на нульове значення
    gamma_complex /= np.abs(gamma_complex[len(tau_vector)//2])
    
    visibility = np.abs(gamma_complex)
    path_difference_um = tau_vector * c * 1e6
    intensity_signal = 1.0 + np.real(gamma_complex)
    
    return path_difference_um, visibility, intensity_signal

# Демонстрація розрахунку для світлодіода LED (630 нм, FWHM = 30 нм)
nu, spec = generate_spectrum(wavelength_center_nm=630, fwhm_nm=30, profile='gaussian')
path_um, vis, I_sig = compute_interferogram(nu, spec, max_delay_fs=200, steps=500)

lc_theory_um = (630e-9)**2 / (30e-9) * 1e6
print(f"Теоретична довжина когерентності L_c: {lc_theory_um:.2f} мкм")
print(f"Максимальна видність при zero delay: V_max = {np.max(vis):.4f}")
