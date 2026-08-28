import numpy as np

def response(g, mu, f, zeta, zeta_s=0.0):
    """Розмах головної маси |X₁| (у частках статичного прогину) на кожній частоті.
    g = ω/ω_p, f = ωₐ/ω_p, μ = m/M, zeta = c/(2mω_p), zeta_s — структурне загасання вежі."""
    w = np.atleast_1d(np.asarray(g, dtype=float))
    X1 = np.empty_like(w, dtype=complex)
    k, c, cs = mu*f*f, 2*zeta*mu, 2*zeta_s          # бо M=K=ω_p=1  ⇒  m=μ, k=μf²
    for n, om in enumerate(w):
        jom = 1j*om
        A = np.array([[1 + jom*cs - om*om + k + jom*c, -(k + jom*c)],
                      [-(k + jom*c),                    k + jom*c - om*om*mu]])
        X1[n] = np.linalg.solve(A, [1.0, 0.0])[0]   # розв'язати 2×2, узяти X₁
    return np.abs(X1)
