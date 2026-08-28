def caret_window(v):
    maj, min_, pat = (int(x) for x in v.split("."))
    if maj > 0:
        return (maj, min_, pat), (maj + 1, 0, 0)      # >=v, <(maj+1).0.0
    if min_ > 0:
        return (maj, min_, pat), (maj, min_ + 1, 0)   # 0.x: стеля — наступний мінор
    return (maj, min_, pat), (maj, min_, pat + 1)     # 0.0.x: кожна латка ламка

def resolve(available, lo, hi):
    ok = [v for v in available if lo <= v < hi]
    return max(ok) if ok else None   # npm/Cargo: найвища; Go MVS узяв би min(ok)

lo, hi = caret_window("2.1.0")
print(resolve([(2, 1, 0), (2, 1, 1), (2, 2, 0), (3, 0, 0)], lo, hi))  # (2, 2, 0)
