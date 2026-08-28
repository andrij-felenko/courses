import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

# Фізичні константи
H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
K_BOLTZ = 1.380649e-23
SIGMA_SB = 5.670374e-8

def planck_radiance(lambda_m, T):
    """Векторизована спектральна яскравість Планка B_λ(λ, T)."""
    c1 = 2.0 * H_PLANCK * C_LIGHT**2
    c2 = (H_PLANCK * C_LIGHT) / K_BOLTZ
    
    x = c2 / (lambda_m * T)
    # Використовуємо np.expm1 для чисельної стабільності
    denom = np.expm1(x)
    
    # Маскуємо випадок переповнення експоненти
    with np.errstate(over='ignore', divide='ignore'):
        val = c1 / ((lambda_m**5) * denom)
        val = np.where(x > 700.0, 0.0, val)
    return val

def analyze_blackbody(T):
    """Комплексний аналіз випромінювання при температурі T."""
    # Пошук піка Віна через оптимізацію
    res = minimize_scalar(lambda lam: -planck_radiance(lam, T), bounds=(1e-9, 1e-3), method='bounded')
    lam_peak = res.x
    
    # Адаптивне інтегрування SciPy quad
    radiance_integral, _ = quad(lambda lam: planck_radiance(lam, T), 1e-8, 1e-4)
    emittance = np.pi * radiance_integral
    expected_emittance = SIGMA_SB * (T**4)
    
    print(f"--- Результати симуляції (Python) для T = {T} K ---")
    print(f"Пікова довжина хвилі λ_max: {lam_peak * 1e9:.2f} нм")
    print(f"Обчислена випромінювальна здатність: {emittance:.4e} Вт/м²")
    print(f"Теоретична (Стефан-Больцман):         {expected_emittance:.4e} Вт/м²")

if __name__ == "__main__":
    analyze_blackbody(5778.0)
