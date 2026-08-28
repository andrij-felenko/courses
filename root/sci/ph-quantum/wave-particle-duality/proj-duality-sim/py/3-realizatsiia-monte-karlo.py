import numpy as np

def calculate_probability(y, wavelength=0.167e-9, slit_d=1.0e-6, slit_b=0.2e-6, screen_D=0.5):
    """Обчислення густини ймовірності влучання електронів P(y)."""
    alpha = (np.pi * slit_d * y) / (wavelength * screen_D)
    beta = (np.pi * slit_b * y) / (wavelength * screen_D)
    
    interference = np.cos(alpha) ** 2
    diffraction = np.sinc(beta / np.pi) ** 2
    return interference * diffraction

def run_monte_carlo_electrons(total_electrons=100000, num_bins=100):
    """Генерація попоштучних влучань методому фон Неймана."""
    screen_half_width = 0.002 # 2 мм
    accepted_y = []
    
    rng = np.random.default_rng(42)
    
    while len(accepted_y) < total_electrons:
        batch_size = (total_electrons - len(accepted_y)) * 2
        y_cand = rng.uniform(-screen_half_width, screen_half_width, size=batch_size)
        u = rng.uniform(0.0, 1.0, size=batch_size)
        
        probs = calculate_probability(y_cand)
        valid = y_cand[u <= probs]
        accepted_y.extend(valid)
        
    accepted_y = np.array(accepted_y[:total_electrons])
    counts, bin_edges = np.histogram(accepted_y, bins=num_bins, range=(-screen_half_width, screen_half_width))
    return counts, bin_edges

if __name__ == "__main__":
    electron_count = 100000
    counts, bin_edges = run_monte_carlo_electrons(electron_count)
    
    print(f"=== Монте-Карло симуляція двохщілинного досліду ({electron_count} електронів) ===")
    for i in range(0, len(counts), 4):
        y_mm = (bin_edges[i] + bin_edges[i+1]) * 500.0
        bar = "#" * (counts[i] // 500)
        print(f"{y_mm:+6.2f} мм | {bar} ({counts[i]})")
