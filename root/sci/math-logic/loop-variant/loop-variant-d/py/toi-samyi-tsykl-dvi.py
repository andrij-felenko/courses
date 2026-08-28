def bsearch(a, target):
    lo, hi = 0, len(a)              # вікно [lo, hi) — де ще може бути ціль
    while lo < hi:
        v = hi - lo                 # варіант — ширина вікна
        mid = lo + (hi - lo) // 2   # так, а не (lo+hi)//2: різниці нема з чого переповнитись
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1            # ціль правіше: відкидаємо ліву половину разом з mid
        else:
            hi = mid                # ціль лівіше: відкидаємо праву половину разом з mid
        assert hi - lo < v          # вікно строго звузилось
    return -1
