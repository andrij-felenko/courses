from scipy.optimize import minimize_scalar, brentq

def peaks(mu, f, zeta):
    """Висоти лівого й правого піків відгуку (западина між ними — коло g ≈ f)."""
    g = np.linspace(0.5, 1.5, 4000)
    A = response(g, mu, f, zeta)
    i0 = int(np.argmin(np.abs(g - f)))          # індекс западини
    return A[:i0+1].max(), A[i0:].max()

def optimal_tuning(mu):
    def best_zeta(f):                            # для даного f — ζ, що мінімізує вищий пік
        z = minimize_scalar(lambda z: max(peaks(mu, f, z)),
                            bounds=(1e-3, 0.5), method='bounded').x
        lo, hi = peaks(mu, f, z)
        return z, lo, hi
    # зовнішній пошук: f, за якого два піки зрівнялись
    f_star = brentq(lambda f: best_zeta(f)[1] - best_zeta(f)[2], 0.80, 1.05)
    z_star, lo, hi = best_zeta(f_star)
    return f_star, z_star, max(lo, hi)

for mu in (0.02, 0.05, 0.10):
    fs, zs, pk = optimal_tuning(mu)
    print(f"μ={mu}: код f={fs:.4f} ζ={zs:.4f} пік={pk:.3f}")
