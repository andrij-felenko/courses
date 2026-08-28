import numpy as np

def generate_flicker_noise(num_samples: int, sample_rate: float) -> np.ndarray:
    """Генерація часового ряду фліккер-шуму 1/f методом зворотного FFT."""
    # Генерація випадкових фаз та білого шуму в частотній області
    freqs = np.fft.rfftfreq(num_samples, d=1.0 / sample_rate)
    freqs[0] = freqs[1]  # Попередження ділення на нуль для DC-компоненти
    
    # Амплітуда спадає як 1/sqrt(f), що дає потужність 1/f
    amplitude_weights = 1.0 / np.sqrt(freqs)
    amplitude_weights[0] = 0.0  # Усунення постійного зміщення
    
    phases = np.random.uniform(0, 2 * np.pi, len(freqs))
    complex_spectrum = amplitude_weights * np.exp(1j * phases)
    
    # Зворотне FFT для отримання часового ряду
    noise_time_series = np.fft.irfft(complex_spectrum, n=num_samples)
    return noise_time_series / np.std(noise_time_series)
