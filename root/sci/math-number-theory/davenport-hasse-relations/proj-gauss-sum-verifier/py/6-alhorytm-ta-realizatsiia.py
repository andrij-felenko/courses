def verify_multiplicative_relation(p=7, m=3):
    """
    Перевірка мультиплікативного співвідношення Девенпорта-Хассе для m=3 у F_7.
    """
    g_gen = 3
    
    # Характер порядка 6 (χ)
    def chi_6(x):
        if x % p == 0: return 0.0 + 0.0j
        val = x % p
        curr = 1; k = 0
        while curr != val and k < p - 1:
            curr = (curr * g_base) % p; k += 1
        return cmath.exp(1j * 2.0 * math.pi * k / 6.0)

    # Характер порядка 3 (θ)
    def theta_3(x):
        if x % p == 0: return 0.0 + 0.0j
        val = x % p
        curr = 1; k = 0
        while curr != val and k < p - 1:
            curr = (curr * g_base) % p; k += 1
        return cmath.exp(1j * 2.0 * math.pi * (k % 3) / 3.0)

    def psi(x):
        return cmath.exp(1j * 2.0 * math.pi * (x % p) / p)

    def gauss_sum(char_fn):
        return sum(char_fn(x) * psi(x) for x in range(1, p))

    # 1. Ліва частина: Добуток 3 сум Гаусса зі зсувом характерів
    lhs = 1.0 + 0.0j
    for a in range(m):
        def shifted_char(x, shift=a):
            return chi_6(x) * (theta_3(x) ** shift)
        lhs *= gauss_sum(shifted_char)

    # 2. Права частина: χ(m^-m) * g(χ^m, ψ) * ∏ g(θ^a, ψ)
    # m^-m mod 7 = 3^-3 mod 7 = 6 mod 7
    m_inv_m = 6
    factor_chi = chi_6(m_inv_m)
    
    def chi_cubed(x):
        return chi_6(x) ** m

    g_chi_m = gauss_sum(chi_cubed)
    
    prod_theta = 1.0 + 0.0j
    for a in range(1, m):
        def theta_pow(x, pow_a=a):
            return theta_3(x) ** pow_a
        prod_theta *= gauss_sum(theta_pow)

    rhs = factor_chi * g_chi_m * prod_theta
    diff = abs(lhs - rhs)

    print(f"\n[Мультиплікативне співвідношення] LHS = {lhs:.5f}")
    print(f"[Мультиплікативне співвідношення] RHS = {rhs:.5f}")
    print(f"Різниця |LHS - RHS| = {diff:.9e}")

if __name__ == "__main__":
    verify_multiplicative_relation(p=7, m=3)
