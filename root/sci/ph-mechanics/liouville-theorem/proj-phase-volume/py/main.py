import math
import numpy as np

def simulate_phase_volume(steps=1000, dt=0.05, num_particles=500):
    # Початковий хмара точок у фазовому просторі: коло радіуса R = 0.2 біля (1.0, 0.0)
    angles = np.linspace(0, 2 * math.pi, num_particles, endpoint=False)
    r = 0.2
    
    # Створюємо початкові координати та імпульси
    q_explicit = 1.0 + r * np.cos(angles)
    p_explicit = 0.0 + r * np.sin(angles)
    
    q_implicit = np.copy(q_explicit)
    p_implicit = np.copy(p_explicit)
    
    q_sympl = np.copy(q_explicit)
    p_sympl = np.copy(p_explicit)
    
    def calculate_area(q, p):
        # Площа полігона у фазовому просторі за формулою Гаусса (галасових шнурків)
        return 0.5 * np.abs(np.dot(q, np.roll(p, 1)) - np.dot(p, np.roll(q, 1)))

    initial_area = calculate_area(q_explicit, p_explicit)
    print(f"Початкова площа фазової хмари Ω₀ = {initial_area:.6f}\n")
    print(f"{'Крок':>5} | {'Явний Ейлер':>14} | {'Неявний Ейлер':>14} | {'Симплектичний':>14}")
    print("-" * 55)

    for step in range(1, steps + 1):
        # 1. Явний Ейлер
        q_exp_new = q_explicit + p_explicit * dt
        p_exp_new = p_explicit - q_explicit * dt
        q_explicit, p_explicit = q_exp_new, p_exp_new

        # 2. Неявний Ейлер
        denom = 1.0 + dt * dt
        q_imp_new = (q_implicit + dt * p_implicit) / denom
        p_imp_new = (p_implicit - dt * q_implicit) / denom
        q_implicit, p_implicit = q_imp_new, p_imp_new

        # 3. Симплектичний Ейлер-Кромер
        p_sym_new = p_sympl - q_sympl * dt
        q_sym_new = q_sympl + p_sym_new * dt
        q_sympl, p_sympl = q_sym_new, p_sym_new

        if step % 200 == 0:
            area_exp = calculate_area(q_explicit, p_explicit)
            area_imp = calculate_area(q_implicit, p_implicit)
            area_sym = calculate_area(q_sympl, p_sympl)
            print(f"{step:5d} | {area_exp:14.6f} | {area_imp:14.6f} | {area_sym:14.6f}")

if __name__ == '__main__':
    simulate_phase_volume()
