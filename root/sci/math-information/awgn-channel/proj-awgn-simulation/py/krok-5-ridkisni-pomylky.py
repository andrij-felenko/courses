def ber_bpsk_until(EbN0_dB, rng, target_errors=100,
                   chunk=200_000, max_bits=200_000_000):
    sigma = sqrt(1.0 / (2 * 10 ** (EbN0_dB / 10.0)))   # BPSK: σ² = N₀/2 = 1/(2·Eb/N₀)
    n_err = n_tot = 0
    while n_err < target_errors and n_tot < max_bits:
        bits = rng.integers(0, 2, chunk)
        rx = (1.0 - 2.0*bits) + sigma*rng.standard_normal(chunk)
        n_err += int(np.count_nonzero((rx < 0) != bits))
        n_tot += chunk
    return n_err / n_tot, n_err, n_tot
