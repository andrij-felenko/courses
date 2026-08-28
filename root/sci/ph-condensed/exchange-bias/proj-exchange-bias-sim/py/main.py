import math

def simulate_exchange_bias():
    # Фізичні параметри гетероструктури FM/AFM
    Ms = 800.0       # emu/cm3 (намагніченість CoFe)
    t_FM = 5.0e-7    # см (5 нм)
    K_FM = 1.0e4     # erg/cm3 (анізотропія FM)
    J_EB = 0.15      # erg/cm2 (обмінна енергія інтерфейсу)
    phi_AFM = 0.0    # рад (зафіксований кут спінів AFM)
    psi_field = 0.0  # рад (напрямок зовнішнього поля)

    H_EB_theory = J_EB / (Ms * t_FM)
    print(f"Теоретичне поле зміщення H_EB: {H_EB_theory:.2f} Oe\n")

    def energy(theta, H_ext):
        e_zeeman = -H_ext * Ms * t_FM * math.cos(theta - psi_field)
        e_anis = K_FM * t_FM * (math.sin(theta) ** 2)
        e_exch = -J_EB * math.cos(theta - phi_AFM)
        return e_zeeman + e_anis + e_exch

    def find_min_theta(H_ext, init_theta):
        best_theta = init_theta
        min_e = energy(init_theta, H_ext)
        for deg in range(-90, 91):
            t = (init_theta + math.radians(deg)) % (2 * math.pi)
            e = energy(t, H_ext)
            if e < min_e:
                min_e = e
                best_theta = t
        return best_theta

    H_max = 800.0
    steps = 80
    dh = (2 * H_max) / steps

    results = []
    cur_theta = psi_field

    # Зворотний хід: +H_max -> -H_max
    for i in range(steps + 1):
        H = H_max - i * dh
        cur_theta = find_min_theta(H, cur_theta)
        results.append((H, math.cos(cur_theta - psi_field), cur_theta))

    # Прямий хід: -H_max -> +H_max
    for i in range(steps + 1):
        H = -H_max + i * dh
        cur_theta = find_min_theta(H, cur_theta)
        results.append((H, math.cos(cur_theta - psi_field), cur_theta))

    print("--- Результати розрахунку (перші 10 точок) ---")
    print("  H (Oe)    |  M / Ms  |  Theta (град)")
    print("------------+----------+--------------")
    for H, m, t in results[:10]:
        print(f"{H:9.2f}   |  {m:6.2f}  |  {math.degrees(t):9.2f}")

if __name__ == "__main__":
    simulate_exchange_bias()
