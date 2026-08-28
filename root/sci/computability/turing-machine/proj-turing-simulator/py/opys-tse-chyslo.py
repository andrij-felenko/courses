ABC = "␣0123XYqacrLR"

def to_number(desc):
    n = 0
    for ch in desc:
        n = n * 13 + ABC.index(ch) + 1
    return n

def from_number(n):
    out = ""
    while n:
        n, r = divmod(n - 1, 13)
        out = ABC[r] + out
    return out
