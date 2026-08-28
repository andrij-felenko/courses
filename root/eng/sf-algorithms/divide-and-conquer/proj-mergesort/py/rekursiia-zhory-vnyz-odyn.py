CUTOFF = 32                            # шматки ≤ 32 добиваємо вставками

def insertion_sort(a, lo, hi):
    for i in range(lo + 1, hi):
        key = a[i]
        j = i - 1
        while j >= lo and a[j] > key:  # > (не ≥) — рівні не переставляємо (стійкість)
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = key

def _sort(a, buf, lo, hi):
    if hi - lo <= CUTOFF:              # дрібний шматок — простим сортуванням
        insertion_sort(a, lo, hi)
        return
    mid = lo + (hi - lo) // 2          # НЕ (lo+hi)//2 — про це нижче
    _sort(a, buf, lo, mid)             # підкорити ліву
    _sort(a, buf, mid, hi)             # підкорити праву
    if a[mid - 1] <= a[mid]:           # уже впорядковано на стику → злиття зайве
        return
    merge(a, buf, lo, mid, hi)         # поєднати

def merge_sort(a):
    buf = list(a)                      # буфер розміру n, виділений ОДИН раз
    _sort(a, buf, 0, len(a))
    return a
