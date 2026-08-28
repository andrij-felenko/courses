def edit_distance(a, b):
    def rec(i, j):
        if i == 0:                              # порожній префікс A → вставити весь B
            return j
        if j == 0:                              # порожній префікс B → видалити весь A
            return i
        if a[i - 1] == b[j - 1]:                # останні символи збіглися — правки нема
            return rec(i - 1, j - 1)
        return 1 + min(rec(i - 1, j),           # видалити a[i-1]
                       rec(i, j - 1),           # вставити b[j-1]
                       rec(i - 1, j - 1))       # замінити a[i-1] на b[j-1]
    return rec(len(a), len(b))
