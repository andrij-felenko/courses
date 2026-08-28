rng = np.random.default_rng(1)
h = np.array([1, 0, .7+.4j, 0, 0, .5-.3j, 0, 0, .35+.2j, 0, 0, .25], complex)
h /= np.sqrt(np.sum(np.abs(h)**2))        # канал одиничної енергії, розкид 11 відліків
H = np.fft.fft(h, N)                       # його частотний відгук

def ber(L, snr_db, n_sym=5000):
    bits = rng.integers(0, 2, (n_sym, N, 2))
    stream = np.concatenate([tx(bits[i], L) for i in range(n_sym)])
    y = np.convolve(stream, h)[:len(stream)]                          # багатопроменевість
    s2 = 10**(-snr_db/10)                                             # шум під заданий SNR
    y = y + np.sqrt(s2/2)*(rng.standard_normal(len(y)) + 1j*rng.standard_normal(len(y)))
    M = L + N
    err = sum(np.sum(rx(y[i*M:(i+1)*M], L, H) != bits[i]) for i in range(n_sym))
    return err / (n_sym * N * 2)

for snr in (0, 8, 16, 24):
    print(f"{snr:2d} дБ   з CP=16: {ber(16, snr):.1e}   без CP: {ber(0, snr):.1e}")
