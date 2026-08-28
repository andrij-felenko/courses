import numpy as np

def simulate_thermal_noise(R=10000.0, T=300.0, C=1e-11, fs=1e7, N=1000000):
    """
    Чисельне моделювання теплового шуму резистора R та його фільтрації RC-колом.
    
    Параметри:
      R  : активний опір, Ом (за замовчуванням 10 кОм)
      T  : абсолютна температура, Кельвіни (за замовчуванням 300 К)
      C  : ємність конденсатора, Фаради (за замовчуванням 10 пФ)
      fs : частота дискретизації, Герци (за замовчуванням 10 МГц)
      N  : кількість дискретних відліків часу (за замовчуванням 1 000 000)
    """
    kB = 1.380649e-23
    dt = 1.0 / fs
    
    # 1. Дисперсія генератора білого шуму в часовій області
    sigma_v = np.sqrt(2.0 * kB * T * R * fs)
    white_noise = np.random.normal(0.0, sigma_v, N)
    
    # 2. RC-фільтрація першого порядку у часовій області
    alpha = np.exp(-dt / (R * C))
    filtered_noise = np.zeros(N)
    for i in range(1, N):
        filtered_noise[i] = alpha * filtered_noise[i-1] + (1.0 - alpha) * white_noise[i]
    
    # 3. Обчислення емпіричної дисперсії filtered-сигналу
    var_theoretical = kB * T / C
    var_empirical = np.var(filtered_noise)
    rel_error = abs(var_empirical - var_theoretical) / var_theoretical * 100.0
    
    print(f"=== Результати моделювання теплового шуму (Python/NumPy) ===")
    print(f"Опір R = {R/1000:.1f} кОм, Ємність C = {C*1e12:.1f} пФ, Температура T = {T} К")
    print(f"Теоретична дисперсія <U^2> = k_B T / C : {var_theoretical:.6e} V^2")
    print(f"Емпірична дисперсія на виході RC-кола  : {var_empirical:.6e} V^2")
    print(f"Відносна похибка моделювання           : {rel_error:.2f}%\n")

if __name__ == "__main__":
    simulate_thermal_noise()
