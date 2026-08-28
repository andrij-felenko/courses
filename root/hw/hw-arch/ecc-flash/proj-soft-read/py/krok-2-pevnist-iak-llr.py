def Phi(x):
    return 0.5 * (1.0 + erf(x / sqrt(2)))

def band_llr_table(edges, sigma):
    # точний LLR кожної смуги між зсунутими лініями read-retry
    lo = np.concatenate(([-np.inf], edges))
    hi = np.concatenate((edges, [np.inf]))
    out = []
    for a, b in zip(lo, hi):
        p0 = (1.0 if b == np.inf else Phi((b-MU0)/sigma)) - (0.0 if a == -np.inf else Phi((a-MU0)/sigma))
        p1 = (1.0 if b == np.inf else Phi((b-MU1)/sigma)) - (0.0 if a == -np.inf else Phi((a-MU1)/sigma))
        out.append(log(p0 / p1))
    return np.array(out)

RETRY = np.array([-1.2, -0.6, 0.0, 0.6, 1.2])   # ×σ навколо межі; центр = тверде читання
