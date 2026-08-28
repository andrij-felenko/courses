import numpy as np

def compute_mutual_information(signal: np.ndarray, max_delay: int = 50, n_bins: int = 32) -> np.ndarray:
    """
    Обчислення середньої взаємної інформації I(p) для затримок від 1 до max_delay.
    """
    n = len(signal)
    mi_values = np.zeros(max_delay)
    
    # Нормалізація сигналу в діапазон [0, 1]
    s_min, s_max = np.min(signal), np.max(signal)
    if s_max == s_min:
        return mi_values
    norm_signal = (signal - s_min) / (s_max - s_min)
    
    for p in range(1, max_delay + 1):
        x = norm_signal[:-p]
        y = norm_signal[p:]
        
        # Дискретизація за гістограмою
        bins_x = np.minimum((x * n_bins).astype(int), n_bins - 1)
        bins_y = np.minimum((y * n_bins).astype(int), n_bins - 1)
        
        # Двовимірна гістограма спільних ймовірностей
        hist_2d = np.zeros((n_bins, n_bins), dtype=np.float64)
        for bx, by in zip(bins_x, bins_y):
            hist_2d[bx, by] += 1.0
        
        hist_2d /= len(x)
        
        # Маргінальні ймовірності
        px = np.sum(hist_2d, axis=1)
        py = np.sum(hist_2d, axis=0)
        
        # Обчислення суми взаємної інформації
        mi = 0.0
        for i in range(n_bins):
            for j in range(n_bins):
                if hist_2d[i, j] > 0 and px[i] > 0 and py[j] > 0:
                    mi += hist_2d[i, j] * np.log2(hist_2d[i, j] / (px[i] * py[j]))
        
        mi_values[p - 1] = mi
        
    return mi_values
