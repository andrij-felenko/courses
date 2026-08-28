# перехресна перевірка: лишити тільки взаємні пари.
# fwd — результат orb_match_all(A, B, ...); повертає список пар і кількість взаємних.
def orb_cross_check(A: list[int], B: list[int], fwd: list[OrbMatch]):
    out = [OrbMatch(query=i) for i in range(len(A))]
    kept = 0
    for i in range(len(A)):
        j = fwd[i].train                         # кого A[i] обрала вперед
        if j < 0:                                # вперед пари не було
            continue

        # кого B[j] обирає назад у A — тут БЕЗ проби відношення, лише найкращий
        back_i, _, _ = orb_two_best(B[j], A)

        if back_i == i:                          # взаємний вибір!
            out[i].train = j
            out[i].dist = fwd[i].dist
            kept += 1
    return out, kept
