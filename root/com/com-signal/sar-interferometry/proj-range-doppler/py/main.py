import numpy as np

def range_doppler_sar_simulation():
    # Параметри радара
    c = 299792458.0
    f0 = 9.6e9            # 9.6 ГГц (X-діапазон)
    wavelength = c / f0
    bw = 100.0e6          # 100 МГц смуга (1.5 м роздільність)
    tp = 10.0e-6          # 10 мкс
    fs = 120.0e6          # 120 МГц
    v = 150.0             # 150 м/с
    prf = 500.0           # 500 Гц
    r0 = 3000.0           # 3000 м
    kr = bw / tp

    n_rg = 256
    n_az = 256

    dt = 1.0 / fs
    d_eta = 1.0 / prf

    tau = np.linspace(-n_rg//2, n_rg//2 - 1, n_rg) * dt + 2 * r0 / c
    eta = np.linspace(-n_az//2, n_az//2 - 1, n_az) * d_eta

    # 1. Генерація сирих даних
    raw = np.zeros((n_az, n_rg), dtype=complex)
    for i, e in enumerate(eta):
        r_eta = np.sqrt(r0**2 + (v * e)**2)
        tau_0 = 2 * r_eta / c
        t_diff = tau - tau_0
        mask = np.abs(t_diff) <= tp / 2
        phase = -2 * np.pi * f0 * tau_0 + np.pi * kr * (t_diff**2)
        raw[i, mask] = np.exp(1j * phase[mask])

    # 2. Стиснення за дальністю (Range Compression)
    f_tau = np.linspace(-fs//2, fs//2 - 1, n_rg) * (fs / n_rg)
    h_range = np.zeros(n_rg, dtype=complex)
    mask_bw = np.abs(f_tau) <= bw / 2
    h_range[mask_bw] = np.exp(1j * np.pi * (f_tau[mask_bw]**2) / kr)

    s_rc = np.fft.ifft(np.fft.fft(raw, axis=1) * h_range, axis=1)

    # 3. Перехід у Range-Doppler простір
    s_rd = np.fft.fft(s_rc, axis=0)

    # 4. Корекція міграції дальності (RCMC)
    f_eta = np.linspace(-prf//2, prf//2 - 1, n_az) * (prf / n_az)
    dr = c / (2 * fs)
    s_rcmc = np.zeros_like(s_rd)
    for i, fe in enumerate(f_eta):
        delta_r = (wavelength**2 * r0 * fe**2) / (8 * v**2)
        shift_bins = delta_r / dr
        # Зсув у спектральній області або інтерполяція
        s_rcmc[i, :] = np.interp(np.arange(n_rg) + shift_bins, np.arange(n_rg), s_rd[i, :], left=0, right=0)

    # 5. Азимутальне стиснення
    val = np.clip((wavelength * f_eta) / (2 * v), -0.999, 0.999)
    az_ref = np.exp(1j * (4 * np.pi * r0 / wavelength) * np.sqrt(1 - val**2))
    s_focused = np.fft.ifft(s_rcmc * az_ref[:, np.newaxis], axis=0)

    peak_idx = np.unravel_index(np.argmax(np.abs(s_focused)), s_focused.shape)
    print(f"[Python-RDA] Точка фокусування: азимут={peak_idx[0]}, дальність={peak_idx[1]}")
    return s_focused
