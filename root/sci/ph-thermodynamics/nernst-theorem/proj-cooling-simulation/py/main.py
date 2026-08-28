import math

R_GAS = 8.314462618
MU_B = 9.274010078e-24
K_B = 1.380649e-23

def spin_entropy(T: float, B: float, g: float = 2.0) -> float:
    if T <= 0:
        return 0.0
    y = (g * MU_B * B) / (2.0 * K_B * T)
    if y > 50:
        return 0.0
    return R_GAS * (math.log(2.0 * math.cosh(y)) - y * math.tanh(y))

def lattice_entropy(T: float, theta_d: float = 60.0) -> float:
    if T <= 0:
        return 0.0
    return (4.0 / 5.0) * (math.pi ** 4) * R_GAS * ((T / theta_d) ** 3)

def total_entropy(T: float, B: float, g: float = 2.0, theta_d: float = 60.0) -> float:
    return spin_entropy(T, B, g) + lattice_entropy(T, theta_d)

def simulate_cooling(T_start: float = 4.2, B_max: float = 1.5, B_min: float = 0.001, steps: int = 6):
    current_T = T_start
    print(f"{'Крок':<5} | {'T_start (К)':<12} | {'S (Дж/моль*К)':<16} | {'T_end (К)':<12}")
    print("-" * 55)

    for i in range(1, steps + 1):
        S_target = total_entropy(current_T, B_max)
        
        # Бісекція для знаходження T_end при S = S_target, B = B_min
        low, high = 1e-7, current_T
        for _ in range(60):
            mid = 0.5 * (low + high)
            if total_entropy(mid, B_min) < S_target:
                low = mid
            else:
                high = mid
        T_end = 0.5 * (low + high)

        print(f"{i:<5} | {current_T:<12.6f} | {S_target:<16.6f} | {T_end:<12.6f}")
        current_T = T_end

if __name__ == "__main__":
    simulate_cooling()
