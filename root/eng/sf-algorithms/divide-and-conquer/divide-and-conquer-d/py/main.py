def merge_sort(a):
    if len(a) <= 1:                     # базовий випадок: 0 або 1 елемент
        return a
    mid   = len(a) // 2
    left  = merge_sort(a[:mid])         # підкорити ліву половину
    right = merge_sort(a[mid:])         # підкорити праву половину
    return merge(left, right)           # поєднати

def merge(x, y):
    out, i, j = [], 0, 0
    while i < len(x) and j < len(y):
        if x[i] <= y[j]:                # менша з двох верхівок
            out.append(x[i]); i += 1
        else:
            out.append(y[j]); j += 1
    out.extend(x[i:]); out.extend(y[j:])   # долити рештку тієї купки, що лишилась
    return out
