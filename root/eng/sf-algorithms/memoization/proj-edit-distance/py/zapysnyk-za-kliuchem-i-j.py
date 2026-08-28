def edit_distance(a, b):
    cache = {}                                  # (i, j) → відстань

    def rec(i, j):
        if i == 0:
            return j
        if j == 0:
            return i
        if (i, j) in cache:                     # уже рахували цю клітину?
            return cache[(i, j)]
        if a[i - 1] == b[j - 1]:
            result = rec(i - 1, j - 1)
        else:
            result = 1 + min(rec(i - 1, j),
                             rec(i, j - 1),
                             rec(i - 1, j - 1))
        cache[(i, j)] = result                  # запам'ятай, щоб не рахувати вдруге
        return result

    return rec(len(a), len(b))
