import numpy as np

def simulate_drude(num_particles=100000, tau=2.5e-14, E_x=1.0e4, dt=1.0e-15, steps=200):
    """
    Чисельне моделювання ансамблю Друде методом Монте-Карло у NumPy.
    """
    mass = 9.109e-31     # Маса електрона (кг)
    charge = 1.602e-19   # Заряд електрона (Кл)
    v_th = 1.0e5         # Теплова швидкість (м/с)

    sigma = v_th / np.sqrt(2.0)
    vx = np.random.normal(0, sigma, num_particles)
    vy = np.random.normal(0, sigma, num_particles)

    a_x = -charge * E_x / mass
    p_scatter = 1.0 - np.exp(-dt / tau)

    theoretical_vd = -charge * E_x * tau / mass
    print(f"Теоретична дрейфова швидкість v_d: {theoretical_vd:.4e} м/с")
    print("-" * 55)
    print("Крок\tЧас (фс)\tСимульована v_d (м/с)")

    for step in range(steps + 1):
        if step % 20 == 0:
            mean_vd = np.mean(vx)
            print(f"{step}\t{step * dt * 1e15:.1f} фс\t\t{mean_vd:.4e} м/с")

        # 1. Прискорення полем
        vx += a_x * dt

        # 2. Визначення частинок, що розсіюються
        scattered = np.random.random(num_particles) < p_scatter

        # 3. Перевизначення швидкостей після зіткнення
        num_scattered = np.sum(scattered)
        if num_scattered > 0:
            vx[scattered] = np.random.normal(0, sigma, num_scattered)
            vy[scattered] = np.random.normal(0, sigma, num_scattered)

if __name__ == "__main__":
    simulate_drude()
