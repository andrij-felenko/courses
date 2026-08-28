def flyweight_savings(N, K, s_intr, e, p=8, f=48):
    """Пам'ять двох схем і точка беззбитковості, у байтах."""
    S_full  = s_intr + e
    M_naive = N * S_full
    M_fw    = N * (e + p) + K * (s_intr + f)
    K_star  = N * (s_intr - p) / (s_intr + f)   # гранична к-сть видів
    return {
        "M_наївно":  M_naive,
        "M_легк":    M_fw,
        "стиснення": M_naive / M_fw,
        "K*":        K_star,
        "виграш?":   K < K_star,
    }

# ліс: мільйон дерев, три види, важка сітка (~1 МБ)
print(flyweight_savings(N=1_000_000, K=3, s_intr=1_000_000, e=16))
# M_наївно ≈ 1.0e12,  M_легк ≈ 27e6,  стиснення ≈ 37000,  K* ≈ 999944,  виграш? True

# те саме, але внутрішній стан — крихітне 4-байтне число:
print(flyweight_savings(N=1_000_000, K=1000, s_intr=4, e=0))
# M_легк > M_наївно,  K* < 0  →  виграш? False: ділити легше за вказівник немає сенсу
