# Побудова скінченної групи й перевірка теореми Лагранжа.
# Рушій нічого не знає про природу елементів — лише про операцію op.

def closure(gens, op):
    """Замкнути твірні за операцією: уся породжена група."""
    G = set(gens)
    frontier = list(gens)
    while frontier:
        fresh = []
        for a in list(G):
            for b in frontier:
                for x in (op(a, b), op(b, a)):
                    if x not in G:
                        G.add(x)
                        fresh.append(x)
        frontier = fresh
    return G

def order(g, op, e):
    """Порядок елемента: найменше m>0 з gᵐ = e."""
    x, m = g, 1
    while x != e:
        x = op(x, g)
        m += 1
    return m

def left_cosets(G, H, op):
    """Ліві суміжні класи gH, здедупльовані як множини."""
    seen, cosets = set(), []
    for g in sorted(G):
        c = frozenset(op(g, h) for h in H)
        if c not in seen:
            seen.add(c)
            cosets.append(c)
    return cosets

def lagrange(G, H, op):
    idx = len(left_cosets(G, H, op))
    return idx, len(G) == idx * len(H) and len(G) % len(H) == 0

# група 1: симетрії трикутника D₃, елемент = перестановка (кортеж образів)
def pmul(g, h):                         # g після h: (g·h)[i] = g[h[i]]
    return tuple(g[h[i]] for i in range(len(g)))

e3 = (0, 1, 2)
r  = (1, 2, 0)                          # поворот 0→1→2→0
s1 = (0, 2, 1)                          # відбиття, що лишає вершину 0
D3 = closure([r, s1], pmul)
H  = closure([r], pmul)                 # підгрупа поворотів
print("D3: |G| =", len(D3), " порядки:", sorted(order(g, pmul, e3) for g in D3))
print("   Лагранж за ⟨r⟩:", lagrange(D3, H, pmul))    # (2, True)

# група 2: оборотні лишки Z₇*, елемент = ціле; РУШІЙ той самий
def mul7(a, b):
    return (a * b) % 7

Z7 = closure([3], mul7)
H7 = closure([2], mul7)
print("Z7*: |G| =", len(Z7), " порядки:", sorted(order(g, mul7, 1) for g in Z7))
print("   Лагранж за ⟨2⟩:", lagrange(Z7, H7, mul7))   # (2, True)
