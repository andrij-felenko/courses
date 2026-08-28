from math import gcd

def units(n: int) -> list[int]:
    """Вцілілі лишки за модулем n — елементи групи (Z/nZ)*."""
    return [x for x in range(1, n) if gcd(x, n) == 1]

def subgroup(a: int, n: int) -> list[int]:
    """<a> = {1, a, a², …} — циклічна підгрупа, породжена елементом a."""
    H, x = [], 1
    while True:
        H.append(x)
        x = x * a % n
        if x == 1:
            return sorted(H)

def cosets(a: int, n: int) -> list[list[int]]:
    """Розбиття (Z/nZ)* на суміжні класи g·<a>."""
    G, H, seen, out = units(n), subgroup(a, n), set(), []
    for g in G:
        if g in seen:
            continue                       # цей g уже накритий чужим класом
        c = sorted(g * h % n for h in H)
        out.append(c)
        seen |= set(c)
    return out

n, a = 15, 2
G, H, cs = units(n), subgroup(a, n), cosets(a, n)
print(G)                                   # [1, 2, 4, 7, 8, 11, 13, 14] — φ(15) = 8
print(H)                                   # [1, 2, 4, 8] — порядок 4
print(cs)                                  # [[1, 2, 4, 8], [7, 11, 13, 14]]

assert sum(len(c) for c in cs) == len(G)          # плитки вкривають усе
assert all(len(c) == len(H) for c in cs)          # плитки однакові
assert len(G) % len(H) == 0                       # Лагранж: |H| ділить |G|
assert pow(a, len(G), n) == 1                     # звідси й теорема Ейлера

for m in range(2, 200):                    # те саме на двох сотнях модулів
    for b in units(m):
        assert len(units(m)) % len(subgroup(b, m)) == 0
        assert pow(b, len(units(m)), m) == 1
