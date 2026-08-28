import numpy as np
N = 64                                    # піднесних = розмір FFT

def qpsk_map(bits):                       # (N,2) біт → (N,) комплексних символів
    return ((1 - 2*bits[:, 0]) + 1j*(1 - 2*bits[:, 1])) / np.sqrt(2)

def qpsk_slice(s):                        # (N,) символів → (N,2) біт
    return np.stack([s.real < 0, s.imag < 0], axis=1).astype(int)

def tx(bits, L):                          # біти символу → часовий блок з префіксом
    x = np.fft.ifft(qpsk_map(bits)) * np.sqrt(N)
    return np.concatenate([x[N-L:], x])

def rx(block, L, H):                      # блок → біти (zero-forcing за відомим H)
    Y = np.fft.fft(block[L:L+N]) / np.sqrt(N)
    return qpsk_slice(Y / H)
