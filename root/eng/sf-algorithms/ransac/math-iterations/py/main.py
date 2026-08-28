import math

def adaptive_k(N, n, p=0.99, k_cap=100_000):
    """Скільки ще крутити: бюджет перераховують за найкращою згодою на льоту."""
    best, trials, k = 0, 0, k_cap        # поки згоди нема, ŵ = 0 → бюджет нескінченний
    while trials < k:
        best = max(best, run_one_trial())     # 1–4: вибірка → модель → згода → рекорд
        trials += 1
        w_hat = best / N
        if w_hat > 0:
            q = w_hat ** n
            k = min(k_cap, math.ceil(math.log(1 - p) / math.log(1 - q))) if q < 1 else 0
    return trials
