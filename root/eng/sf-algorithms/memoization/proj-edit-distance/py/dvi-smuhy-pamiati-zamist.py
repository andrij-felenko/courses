def edit_distance(a, b):
    m, n = len(a), len(b)
    prev = list(range(n + 1))                   # рядок 0: 0,1,2,…,n
    for i in range(1, m + 1):
        curr = [i] + [0] * n                    # curr[0] = i (видалити i символів A)
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j],       # згори  = видалити
                                  curr[j - 1],   # зліва  = вставити
                                  prev[j - 1])   # діагональ = замінити
        prev = curr                             # поточний стає попереднім
    return prev[n]
