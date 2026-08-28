# зіставити весь набір A з набором B пробою відношення.
# повертає список OrbMatch довжини len(A) та кількість прийнятих пар.
# (пари з train == -1 у списку теж лишаються — щоб зберегти відповідність за query.)
def orb_match_all(A: list[int], B: list[int], ratio: float):
    out = [OrbMatch(query=i) for i in range(len(A))]
    accepted = 0
    for i, query in enumerate(A):
        if not B:                                # порожній набір — нема з чим в'язати
            continue

        j, best, second = orb_two_best(query, B)
        if j >= 0 and orb_pass_ratio(best, second, ratio):
            out[i].train = j
            out[i].dist = best
            accepted += 1
    return out, accepted
