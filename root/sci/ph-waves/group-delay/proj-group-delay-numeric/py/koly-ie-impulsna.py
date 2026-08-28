def group_delay_fir(h, nfft=4096, fs=1.0):
    """Точна групова затримка скінченної імпульсної характеристики."""
    h = np.asarray(h, dtype=float)
    n = np.arange(h.size)
    H = np.fft.rfft(h, nfft)
    R = np.fft.rfft(n * h, nfft)                 # «нахилена» характеристика
    return np.fft.rfftfreq(nfft, 1 / fs), np.real(R / H) / fs

h = np.zeros(41); h[17] = 1.0                    # чиста затримка на 17 відліків
print(group_delay_fir(h)[1][:3])                 # [17. 17. 17.]
