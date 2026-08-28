import math

def casimir_ideal_pressure(d_meters: float) -> float:
    """Обчислення ідеального тиску Казимира між провідниками у Паскалях."""
    hbar = 1.054571817e-34  # Дж·с (зменшена стала Планка)
    c = 299792458.0         # м/с (швидкість світла у вакуумі)
    factor = (math.pi ** 2) * hbar * c / 240.0
    return - factor / (d_meters ** 4)

def lifshitz_correction_factor(d_meters: float, plasma_wave_nm: float = 136.0) -> float:
    """Обчислення коефіцієнта поправки Ліфшиця для золота (Au)."""
    lambda_p = plasma_wave_nm * 1e-9
    # Наближення Друде-Ліфшиця для малих і середніх відстаней
    return 1.0 / (1.0 + 1.2 * (lambda_p / d_meters))

def analyze_casimir_range():
    distances_nm = [10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 5000.0]
    pascal_to_atm = 1.01325e5
    
    print(f"{'d (nm)':>8} | {'P_ideal (Pa)':>14} | {'P_real (Pa)':>14} | {'P_real (atm)':>14} | {'Factor η':>10}")
    print("-" * 72)
    
    for d_nm in distances_nm:
        d_m = d_nm * 1e-9
        p_ideal = casimir_ideal_pressure(d_m)
        eta = lifshitz_correction_factor(d_m)
        p_real = p_ideal * eta
        p_real_atm = abs(p_real) / pascal_to_atm
        
        print(f"{d_nm:8.1f} | {abs(p_ideal):14.4e} | {abs(p_real):14.4e} | {p_real_atm:14.4e} | {eta:10.4f}")

if __name__ == "__main__":
    analyze_casimir_range()
