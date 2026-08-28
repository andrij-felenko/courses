# Доступна ємність (А·год) на струмі load_A з поправкою Пойкерта.
# cap_rated_ah  — паспортна ємність
# i_rated_a     — струм, на якому виміряли паспорт (напр. C/20)
# k             — показник Пойкерта хімії (свинець ~1.3, літій ~1.05)
def peukert_capacity_ah(cap_rated_ah, i_rated_a, load_a, k):
    if load_a <= 0.0:
        return cap_rated_ah                        # без навантаження — увесь запас
    return cap_rated_ah * (i_rated_a / load_a) ** (k - 1.0)


# Оцінка часу до відсічки (год) за сталого струму.
def runtime_hours(cap_rated_ah, i_rated_a, load_a, k):
    cap = peukert_capacity_ah(cap_rated_ah, i_rated_a, load_a, k)
    return cap / load_a                            # а не cap_rated_ah / load_a!
