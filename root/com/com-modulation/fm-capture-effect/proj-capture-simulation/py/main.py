import numpy as np

def simulate_fm_capture(carrier_ratio_db=6.0, fs=480000, duration=0.1):
    """
    Числове моделювання ефекту захоплення ЧМ при накладанні двох сигналів.
    Параметр carrier_ratio_db задає відношення амплітуд A1/A2 у децибелах.
    """
    t = np.arange(int(fs * duration)) / fs
    
    # Сигнал 1 (корисний): тон 400 Гц, девіація 75 кГц
    f_mod1 = 400.0
    dev1 = 75000.0
    phi1 = (dev1 / f_mod1) * np.sin(2 * np.pi * f_mod1 * t)
    s1 = np.exp(1j * phi1)
    
    # Сигнал 2 (завада): тон 1000 Гц, девіація 75 кГц, зсув несучої 5 кГц
    f_mod2 = 1000.0
    dev2 = 75000.0
    f_offset = 5000.0
    phi2 = 2 * np.pi * f_offset * t + (dev2 / f_mod2) * np.sin(2 * np.pi * f_mod2 * t)
    
    a2 = 10.0 ** (-carrier_ratio_db / 20.0)
    s2 = a2 * np.exp(1j * phi2)
    
    # Векторне додавання двох сигналів
    s_sum = s1 + s2
    
    # Амплітудний обмежувач: нормування модуля до 1.0
    s_lim = s_sum / np.abs(s_sum)
    
    # Квадратурний дискримінатор миттєвої частоти
    dphi = np.angle(s_lim[1:] * np.conj(s_lim[:-1]))
    freq_inst = dphi * (fs / (2 * np.pi))
    
    # Вимірювання амплітуд аудіокомпонент 400 Гц та 1000 Гц за допомогою ДФТ
    fft_vals = np.abs(np.fft.rfft(freq_inst))
    fft_freqs = np.fft.rfftfreq(len(freq_inst), 1.0 / fs)
    
    idx1 = np.argmin(np.abs(fft_freqs - f_mod1))
    idx2 = np.argmin(np.abs(fft_freqs - f_mod2))
    
    amp1 = fft_vals[idx1]
    amp2 = fft_vals[idx2]
    
    # Обчислення придушення у децибелах
    suppression_db = 20.0 * np.log10(amp1 / (amp2 + 1e-12))
    
    return carrier_ratio_db, suppression_db, freq_inst

if __name__ == "__main__":
    print("=== Результати моделювання ефекту захоплення ЧМ (Python) ===")
    ratios = [-10.0, -6.0, -2.0, -0.5, 0.5, 2.0, 6.0, 12.0]
    for r in ratios:
        ratio_val, supp_val, _ = simulate_fm_capture(carrier_ratio_db=r)
        captured_str = "Сигнал 1 (400 Гц)" if r > 0 else "Сигнал 2 (1000 Гц)"
        print(f"Співвідношення A1/A2 = {r:5.1f} дБ | Придушення: {supp_val:6.1f} дБ | Захоплено: {captured_str}")
