import math

def servers_for_p99(rate_per_s, service_s, p99_target_s):
    """Скільки серверів (за грубою M/M/1-логікою на сервер),
    щоб P99 часу відповіді не перевищив цілі."""
    # P99 одиночної черги ≈ 4.61 · S / (1 − ρ); звідси стеля ρ:
    rho_max = 1.0 - 4.61 * service_s / p99_target_s
    if rho_max <= 0:
        raise ValueError("ціль по P99 менша за сам час обслуговування — недосяжно")
    # ρ = λ·S / серверів ≤ rho_max
    return math.ceil(rate_per_s * service_s / rho_max)

n = servers_for_p99(rate_per_s=8000, service_s=0.020, p99_target_s=0.200)
# rho_max = 1 − 4.61·0.02/0.2 = 0.539
# серверів = ceil(8000 · 0.02 / 0.539) = ceil(296.8) = 297
