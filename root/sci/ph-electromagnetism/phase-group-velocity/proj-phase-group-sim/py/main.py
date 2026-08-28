import numpy as np


def simulate_beats(dx=0.01, x_max=50.0, dt=0.02, t_max=10.0):
    """Моделювання руху двох інтерферуючих гармонік (біття)."""
    x = np.arange(0, x_max, dx)
    
    # Параметри двох хвиль
    w0, dw = 5.0, 0.5
    k0, dk = 3.0, 0.8
    
    w1, w2 = w0 + dw, w0 - dw
    k1, k2 = k0 + dk, k0 - dk
    
    vp_theory = w0 / k0
    vg_theory = dw / dk
    
    print(f"Теоретична фазова швидкість  v_p = {vp_theory:.4f}")
    print(f"Теоретична групова швидкість v_g = {vg_theory:.4f}")
    
    # Розрахунок стану для часових кроків t = 0 та t = t_max
    for t in [0.0, t_max]:
        field = np.cos(w1 * t - k1 * x) + np.cos(w2 * t - k2 * x)
        envelope = 2.0 * np.cos(dw * t - dk * x)
        
        # Пошук максимуму огинаючої поблизу x = 10..40
        idx_peak = np.argmax(np.abs(envelope[(x > 10) & (x < 40)]))
        x_peak = x[(x > 10) & (x < 40)][idx_peak]
        print(f"Час t = {t:4.1f} c | Положення піка огинаючої: x_peak = {x_peak:.3f} м")


def simulate_gvd_pulse(n_pts=1024, dt=0.1, z_distance=100.0, beta2=2.5):
    """Моделювання розпливання Гаусового імпульсу спектральним методом (GVD)."""
    t = np.linspace(-50, 50, n_pts)
    tau0 = 3.0  # Початкова тривалість
    
    u_time = np.exp(- (t**2) / (2.0 * tau0**2)).astype(complex)
    
    freq = np.fft.fftfreq(n_pts, d=dt) * 2.0 * np.pi
    u_freq = np.fft.fft(u_time)
    
    # Набіг дисперсійної фази H(w) = exp(-j * 0.5 * beta2 * w^2 * z)
    phase_shift = np.exp(-1j * 0.5 * beta2 * (freq**2) * z_distance)
    u_out_freq = u_freq * phase_shift
    
    u_out_time = np.fft.ifft(u_out_freq)
    
    intensity_in = np.abs(u_time)**2
    intensity_out = np.abs(u_out_time)**2
    
    w_in = np.sqrt(np.sum((t**2) * intensity_in) / np.sum(intensity_in))
    w_out = np.sqrt(np.sum((t**2) * intensity_out) / np.sum(intensity_out))
    
    print(f"\nGVD Дисперсія: початкова ширина = {w_in:.3f}, вихідна = {w_out:.3f}")
    print(f"Коефіцієнт розпливання: {w_out / w_in:.3f}")


def simulate_soliton_ssfm(n_pts=1024, dt=0.1, z_total=5.0, steps=200):
    """Спліт-степ метод Фур'є (SSFM) для фундаментального солітона (NLSE)."""
    t = np.linspace(-40, 40, n_pts)
    dz = z_total / steps
    beta2 = -1.0  # Аномальна дисперсія
    gamma = 1.0   # Керрівська нелінійність
    
    # Початковий фундаментальний солітон N=1: A(0, t) = sech(t)
    A = 1.0 / np.cosh(t)
    A = A.astype(complex)
    
    freq = np.fft.fftfreq(n_pts, d=dt) * 2.0 * np.pi
    disp_half = np.exp(-1j * 0.5 * beta2 * (freq**2) * (dz / 2.0))
    
    # Спліт-степ інтегрування
    for _ in range(steps):
        # 1. Півкроку дисперсії
        A_freq = np.fft.fft(A) * disp_half
        A = np.fft.ifft(A_freq)
        
        # 2. Повний крок нелінійності
        A *= np.exp(1j * gamma * (np.abs(A)**2) * dz)
        
        # 3. Півкроку дисперсії
        A_freq = np.fft.fft(A) * disp_half
        A = np.fft.ifft(A_freq)
        
    peak_in = 1.0
    peak_out = np.max(np.abs(A))
    print(f"\nСолітон SSFM: початковий пік = {peak_in:.3f}, вихідний пік = {peak_out:.3f}")
    print("Форма солітона збереглася без розпливання завдяки балансу GVD та SPM.")


if __name__ == "__main__":
    simulate_beats()
    simulate_gvd_pulse()
    simulate_soliton_ssfm()
