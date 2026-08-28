import numpy as np

def run_heterodyne_simulation():
    sample_rate = 1.0e9    # 1 ГВибірок/с
    f_if = 100.0e6         # 100 МГц проміжна частота
    p_signal = 1.0e-9      # 1 нВт сигнальна потужність
    p_lo = 1.0e-3          # 1 мВт потужність гетеродина
    responsivity = 0.85    # А/Вт чутливість фотодіода
    num_samples = 2000

    dt = 1.0 / sample_rate
    t = np.arange(num_samples) * dt

    # Цільовий фазовий стрибок на середині інтервалу (BPSK 0 -> PI/2)
    phase_target = np.where(t > (num_samples * dt / 2.0), np.pi / 2.0, 0.0)

    # Фотострум та дробовий шум
    q_elem = 1.602176634e-19
    i_lo = responsivity * p_lo
    peak_beat = 2.0 * responsivity * np.sqrt(p_signal * p_lo)
    shot_std = np.sqrt(2.0 * q_elem * i_lo * (sample_rate / 2.0))

    # Створення сигналу биття + шум
    beat_signal = peak_beat * np.cos(2.0 * np.pi * f_if * t + phase_target)
    noise = np.random.normal(0.0, shot_std, size=num_samples)
    i_bal = beat_signal + noise

    # Множення на опорні квадратури
    raw_i = i_bal * np.cos(2.0 * np.pi * f_if * t)
    raw_q = i_bal * (-np.sin(2.0 * np.pi * f_if * t))

    # Низькочастотне ковзне усереднення
    win = max(1, int(sample_rate / (f_if * 2.0)))
    kernel = np.ones(2 * win + 1) / (2 * win + 1)
    filtered_i = np.convolve(raw_i, kernel, mode='same')
    filtered_q = np.convolve(raw_q, kernel, mode='same')

    # Відновлення фази
    phase_recovered = np.arctan2(filtered_q, filtered_i)

    print("=== СИМУЛЯЦІЯ ОПТИЧНОГО ГЕТЕРОДИНА (Python) ===")
    print(f"Потужність сигналу P_s: {p_signal:.2e} Вт")
    print(f"Потужність гетеродина P_LO: {p_lo:.2e} Вт")
    print(f"Піковий струм биття: {peak_beat * 1e6:.3f} мкА")
    print(f"СКВ дробового шуму: {shot_std * 1e6:.3f} мкА\n")

    print("Час (мкс) | Відновлена фаза (рад) | Цільова фаза")
    print("-" * 47)
    indices = np.linspace(num_samples // 10, num_samples - num_samples // 10, 5, dtype=int)
    for idx in indices:
        print(f"{t[idx] * 1e6:9.2f} | {phase_recovered[idx]:21.4f} | {phase_target[idx]:12.4f}")

if __name__ == '__main__':
    run_heterodyne_simulation()
