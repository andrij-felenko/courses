def group_delay_ls(f, H, m=11, floor_db=-40.0):
    """Затримка як нахил прямої, підігнаної МНК у вікні з m точок.
    Точки, де |H| провалюється нижче floor_db від максимуму, не беруться:
    там фаза — самий шум. Повертає масив довжини f.size із NaN на краях."""
    f = np.asarray(f, dtype=float)
    H = np.asarray(H, dtype=complex)

    step = np.angle(H[1:] * np.conj(H[:-1]))          # безпечні прирости
    psi = np.concatenate(([0.0], np.cumsum(step)))    # локально розгорнута фаза
    mag = 20.0 * np.log10(np.abs(H) / np.max(np.abs(H)))

    half = m // 2
    tau = np.full(f.size, np.nan)
    for k in range(half, f.size - half):
        sl = slice(k - half, k + half + 1)
        if np.any(mag[sl] < floor_db):                # у провалі АЧХ не рахуємо
            continue
        w = 2.0 * np.pi * f[sl]
        wc = w - w.mean()
        pc = psi[sl] - psi[sl].mean()
        tau[k] = -np.dot(wc, pc) / np.dot(wc, wc)     # нахил прямої МНК
    return tau
