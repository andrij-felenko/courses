import math
import random
import numpy as np

def simulate_lattice_gas(lx=100, ly=100, num_particles=2000, max_steps=500):
    # Початковий стан: усі частинки у лівій половині (x < lx // 2)
    particles = np.zeros((num_particles, 2), dtype=int)
    particles[:, 0] = np.random.randint(0, lx // 2, size=num_particles)
    particles[:, 1] = np.random.randint(0, ly, size=num_particles)

    history_steps = []
    history_nl = []
    history_entropy = []

    s_max = num_particles * math.log(2.0)

    for step in range(max_steps):
        # Підрахунок кількості частинок у лівій половині
        n_left = np.sum(particles[:, 0] < (lx // 2))
        n_right = num_particles - n_left

        # Обчислення S / k_B = ln(N!) - ln(N_L!) - ln(N_R!) через math.lgamma
        s_val = (math.lgamma(num_particles + 1) 
                 - math.lgamma(n_left + 1) 
                 - math.lgamma(n_right + 1))

        history_steps.append(step)
        history_nl.append(n_left)
        history_entropy.append(s_val)

        # Зсув частинок у 4 напрямках
        moves = np.random.choice([0, 1, 2, 3], size=num_particles)
        # 0: right, 1: left, 2: up, 3: down
        dx = np.where(moves == 0, 1, np.where(moves == 1, -1, 0))
        dy = np.where(moves == 2, 1, np.where(moves == 3, -1, 0))

        new_x = np.clip(particles[:, 0] + dx, 0, lx - 1)
        new_y = np.clip(particles[:, 1] + dy, 0, ly - 1)

        particles[:, 0] = new_x
        particles[:, 1] = new_y

    return history_steps, history_nl, history_entropy, s_max

if __name__ == '__main__':
    steps, nl, s_list, s_max = simulate_lattice_gas()
    print(f"Початкова ентропія S(0) / k_B = {s_list[0]:.2f}")
    print(f"Кінцева ентропія S(500) / k_B = {s_list[-1]:.2f}")
    print(f"Теоретичний максимум S_max / k_B = {s_max:.2f}")
