import numpy as np

def compute_polariton_spectrum(
    f_a=10.0e9,        # Власна частота фотонного резонатора (Гц)
    kappa_tot=3.0e6,   # Повні втрати фотонного резонатора κ (Гц)
    kappa_ext=1.5e6,   # Зовнішній зв'язок резонатора з портами κ_ext (Гц)
    gamma_m=1.0e6,     # Згасання магнонів у сферичному зразку YIG γ (Гц)
    g_eff=150.0e6,     # Колективна константа спін-фотонного зв'язку g_eff (Гц)
    gamma_e=28.0e9,    # Гіромагнітне співвідношення електрона (Гц/Тл)
    h_min=0.34,        # Початкове значення статичного магнітного поля (Тл)
    h_max=0.37,        # Кінцеве значення статичного магнітного поля (Тл)
    num_h=250,         # Кількість точок дискретизації по магнітному полю
    num_f=400          # Кількість точок дискретизації по частоті
):
    """
    Обчислює двовимірну карту амплітуди проходження S21(f, H0),
    модові вітки нижнього (LMP) та верхнього (UMP) магнон-поляритонів,
    а також величину вакуумного розщеплення Рабі.
    """
    # 1. Генерація сіток магнітного поля та частот
    h_array = np.linspace(h_min, h_max, num_h)
    f_array = np.linspace(f_a - 3.5 * g_eff, f_a + 3.5 * g_eff, num_f)
    
    f_lmp = np.zeros(num_h)
    f_ump = np.zeros(num_h)
    s21_matrix = np.zeros((num_f, num_h))
    
    kappa_hz = kappa_tot / (2.0 * np.pi)
    gamma_hz = gamma_m / (2.0 * np.pi)
    g_hz = g_eff / (2.0 * np.pi)
    k_ext_hz = kappa_ext / (2.0 * np.pi)
    
    # 2. Обчислення власних частот неермітового гамільтоніана
    for j, h_val in enumerate(h_array):
        f_m = gamma_e * h_val  # Ларморівська частота FMR
        
        # Неермітова матриця 2x2 у частотному поданні
        h_eff = np.array([
            [f_a - 1j * kappa_hz, g_hz],
            [g_hz, f_m - 1j * gamma_hz]
        ], dtype=complex)
        
        # Обчислення комплексних власних значень
        evals = np.linalg.eigvals(h_eff)
        real_evals = np.sort(np.real(evals))
        f_lmp[j] = real_evals[0]
        f_ump[j] = real_evals[1]
        
        # 3. Векторизований розрахунок комплексної амплітуди S21
        denom_m = f_array - f_m + 1j * gamma_hz
        denom_tot = (f_array - f_a + 1j * kappa_hz) - (g_hz**2 / denom_m)
        s21_complex = (-1j * k_ext_hz) / denom_tot
        s21_matrix[:, j] = np.abs(s21_complex)
        
    # 4. Знаходження точки точного резонансу та оцінка розщеплення Рабі
    idx_res = np.argmin(np.abs(gamma_e * h_array - f_a))
    rabi_splitting_hz = f_ump[idx_res] - f_lmp[idx_res]
    
    return {
        "h_array": h_array,
        "f_array": f_array,
        "f_lmp": f_lmp,
        "f_ump": f_ump,
        "s21_matrix": s21_matrix,
        "rabi_mhz": rabi_splitting_hz / 1.0e6
    }

if __name__ == "__main__":
    spectrum = compute_polariton_spectrum()
    print(f"Розрахункове розщеплення Рабі у точці резонансу: {spectrum['rabi_mhz']:.2f} МГц")
