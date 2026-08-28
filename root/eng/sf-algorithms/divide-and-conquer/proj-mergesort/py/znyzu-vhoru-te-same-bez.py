def merge_sort_bottomup(a):
    n = len(a)
    buf = list(a)                          # буфер розміру n, один раз
    width = 1
    while width < n:                       # ширина купок: 1, 2, 4, 8, …
        lo = 0
        while lo < n:
            mid = min(lo + width, n)       # кінець лівої купки
            hi  = min(lo + 2 * width, n)   # кінець правої купки
            if mid < hi:                   # права купка непорожня — є що зливати
                merge(a, buf, lo, mid, hi)
            lo += 2 * width
        width *= 2
    return a
