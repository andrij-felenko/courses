def otsu_threshold(hist, N):
    """hist — гістограма (лічба пікселів), N — усього пікселів.
    Повертає поріг t: пікселі з яскравістю > t — об'єкт."""
    L = len(hist)
    sum_total = sum(i * hist[i] for i in range(L))  # Σ i·n_i по всій гістограмі

    sum_bg = 0                              # накопичений момент S(t)·N
    w_bg = 0                                # накопичена вага w₀·N
    best_var = -1.0
    best_t = 0

    for t in range(L):
        w_bg += hist[t]                     # w₀·N наростанням
        if w_bg == 0:
            continue                        # клас тла ще порожній
        w_fg = N - w_bg                     # w₁·N
        if w_fg == 0:
            break                           # клас об'єкта спорожнів — далі нема сенсу

        sum_bg += t * hist[t]               # S(t)·N наростанням
        mu_bg = sum_bg / w_bg
        mu_fg = (sum_total - sum_bg) / w_fg

        # σ²_b ∝ w₀·w₁·(μ₀−μ₁)²  (спільний дільник N² відкинуто)
        diff = mu_bg - mu_fg
        var_between = w_bg * w_fg * diff * diff

        if var_between > best_var:          # запам'ятати вершину горба
            best_var = var_between
            best_t = t

    return best_t
