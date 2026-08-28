def ber_qpsk(EbN0_dB, n_bits, rng):
    n_bits -= n_bits % 2                       # парне число: 2 біти на символ
    bits = rng.integers(0, 2, n_bits)
    b_i, b_q = bits[0::2], bits[1::2]          # код Грея: один біт на вісь I, другий на Q
    tx = ((1 - 2*b_i) + 1j*(1 - 2*b_q)) / sqrt(2.0)     # 4 точки (±1±j)/√2, Es=1
    sigma = noise_sigma(EbN0_dB, bits_per_symbol=2)
    noise = sigma * (rng.standard_normal(len(tx)) + 1j*rng.standard_normal(len(tx)))
    rx = tx + noise                            # КОМПЛЕКСНИЙ шум: σ окремо в I та в Q
    b_i_hat = (rx.real < 0).astype(int)        # найближчий символ = знак по кожній осі
    b_q_hat = (rx.imag < 0).astype(int)
    bits_hat = np.empty(n_bits, dtype=int)
    bits_hat[0::2], bits_hat[1::2] = b_i_hat, b_q_hat
    return np.count_nonzero(bits_hat != bits) / n_bits
