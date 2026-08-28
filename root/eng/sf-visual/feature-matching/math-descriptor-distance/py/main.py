# пошук найближчого й другого праворуч + проба відношення.
# повертає індекс прийнятого збігу або -1, якщо неоднозначно.
def match_ratio(query, train, ratio):
    best, second, best_j = 1e30, 1e30, -1
    for j, t in enumerate(train):
        d = l2_sq(query, t)                     # працюємо у квадраті
        if d < best:
            second, best, best_j = best, d, j
        elif d < second:
            second = d
    # порівнюємо у КВАДРАТІ: (d₁/d₂ < r) ⇔ (d₁² < r²·d₂²)
    if second > 0.0 and best < ratio * ratio * second:
        return best_j      # відрив достатній — прийняти
    return -1              # майже нічия — відкинути
