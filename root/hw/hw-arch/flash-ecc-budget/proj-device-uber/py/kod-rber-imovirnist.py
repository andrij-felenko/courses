@dataclass(frozen=True)
class Code:
    n: int          # довжина кодового слова, бітів
    t: int          # скільки помилок гарантовано виправляє


BCH_1KIB = Code(n=8752, t=40)      # 1 КіБ даних + 40·14 = 560 бітів парності; рейт 0.936


def word_failure_prob(code: Code, p: float) -> float:
    """P(у слові більше ніж t перевернутих бітів) — точний біноміальний хвіст."""
    if p <= 0.0:
        return 0.0
    n, t = code.n, code.t
    # опора — НАЙБІЛЬШИЙ доданок хвоста (мода біноміала, підтягнута в межі хвоста),
    # інакше exp() від додатної різниці переповниться
    k_peak = min(n, max(t + 1, int((n + 1) * p)))
    ref = _log_term(n, k_peak, p)
    total, k = 0.0, t + 1
    while k <= n:
        rel = _log_term(n, k, p) - ref          # завжди ≤ 0 ⇒ exp() безпечний
        total += exp(rel) if rel > -700.0 else 0.0
        if k >= n * p and rel < -40.0:          # обрив ЛИШЕ за піком, де доданки спадають
            break
        k += 1
    return min(exp(ref + log(total)), 1.0)
