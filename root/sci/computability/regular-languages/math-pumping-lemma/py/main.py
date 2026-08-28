from itertools import product

def words(alphabet, max_len):
    """Усі слова над alphabet завдовжки 0..max_len."""
    for n in range(max_len + 1):
        for t in product(alphabet, repeat=n):
            yield "".join(t)

def index_upto(member, alphabet, k):
    """Скільки РІЗНИХ майбутніх дають префікси завдовжки ≤ k,
    якщо розрізняти їх хвостами завдовжки ≤ k."""
    tails = list(words(alphabet, k))
    seen = {}
    for x in words(alphabet, k):
        sig = tuple(member(x + z) for z in tails)   # ← рядок таблиці = майбутнє x
        seen.setdefault(sig, x)
    return len(seen)

# --- три мови ---
even_ones = lambda w: w.count("1") % 2 == 0        # регулярна

def zeros_ones(w):                                  # 0ⁿ1ⁿ, n ≥ 1
    n = len(w) // 2
    return len(w) >= 2 and len(w) % 2 == 0 and w == "0" * n + "1" * n

import re
_abc = re.compile(r"(a*)(b*)(c*)\Z")

def F(w):                                           # aⁱbʲcᵏ, і якщо i = 1, то j = k
    m = _abc.match(w)
    if not m:
        return False
    i, j, k = (len(g) for g in m.groups())
    return (j == k) if i == 1 else True

print(" k   парн.од.   0ⁿ1ⁿ      F")
for k in range(1, 7):
    print("%2d %8d %7d %6d" % (k,
          index_upto(even_ones,  "01",  k),
          index_upto(zeros_ones, "01",  k),
          index_upto(F,          "abc", k)))
