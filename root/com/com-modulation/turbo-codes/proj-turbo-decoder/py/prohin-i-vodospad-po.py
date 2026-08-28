def experiment(N, EbN0dB, nframes, niters, seed=11):
    rng = random.Random(seed)
    R = 1.0/3.0
    EbN0 = 10**(EbN0dB/10.0)
    sigma = math.sqrt(1.0/(2.0*R*EbN0))
    Lc = 2.0/(sigma*sigma)
    perm, inv = make_interleaver(N, rng)
    errs = [0]*niters
    for _ in range(nframes):
        u = [rng.randint(0, 1) for _ in range(N)]
        sysb, p1, p2 = turbo_encode(u, perm)
        Ls  = bpsk_awgn(sysb, sigma, Lc, rng)
        Lp1 = bpsk_awgn(p1,   sigma, Lc, rng)
        Lp2 = bpsk_awgn(p2,   sigma, Lc, rng)
        hist = turbo_decode(Ls, Lp1, Lp2, perm, inv, niters)
        for it, bits in enumerate(hist):
            errs[it] += sum(1 for k in range(N) if bits[k] != u[k])
    return [e/(nframes*N) for e in errs]

for snr in (0.5, 1.0):
    ber = experiment(N=1024, EbN0dB=snr, nframes=80, niters=10)
    print("%.1f дБ:" % snr, " ".join("%.2e" % b for b in ber))
