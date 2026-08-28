# ─────────── ЧАСТИНА 1: машинка ───────────
from typing import NamedTuple

ZERO, ONE = 0, 1


class Node(NamedTuple):
    var: int
    lo: int
    hi: int


class Bdd:
    def __init__(self, nvars: int) -> None:
        self.nvars = nvars
        self.nodes: list[Node | None] = [None, None]      # 0 і 1 — термінали
        self.unique: dict[Node, int] = {}                 # вузол → його єдиний номер
        self.cache: dict[tuple[str, int, int], int] = {}  # (операція, f, g) → готова відповідь
        self.calls = self.hits = 0

    # Термінал не має змінної: віддаємо «рівень нижче всіх» — так min() працює сам собою.
    def top(self, u: int) -> int:
        return self.nvars if u < 2 else self.nodes[u].var

    # Єдине місце, де народжується вузол. Обидва правила зведення — тут.
    def mk(self, var: int, lo: int, hi: int) -> int:
        if lo == hi:
            return lo                                     # усунення: змінна ні на що не впливає
        node = Node(var, lo, hi)
        if (u := self.unique.get(node)) is not None:
            return u                                      # злиття: такий вузол уже є
        u = len(self.nodes)
        self.nodes.append(node)
        self.unique[node] = u
        return u

    def variable(self, i: int) -> int:
        return self.mk(i, ZERO, ONE)

    def cofactors(self, u: int, var: int) -> tuple[int, int]:
        if self.top(u) != var:
            return u, u                                   # змінної немає — обидві половини ті самі
        return self.nodes[u].lo, self.nodes[u].hi

    @staticmethod
    def _terminal(op: str, f: int, g: int) -> int | None:
        if op == "and":
            if ZERO in (f, g): return ZERO
            if f == ONE: return g
            if g == ONE: return f
            if f == g: return f
        elif op == "or":
            if ONE in (f, g): return ONE
            if f == ZERO: return g
            if g == ZERO: return f
            if f == g: return f
        elif op == "xor":
            if f == ZERO: return g
            if g == ZERO: return f
            if f == g: return ZERO
        return None

    # Розкладання Шеннона, застосоване до пари функцій.
    def apply(self, op: str, f: int, g: int) -> int:
        self.calls += 1
        if (t := self._terminal(op, f, g)) is not None:
            return t
        key = (op, f, g) if f <= g else (op, g, f)        # усі три операції комутативні
        if (r := self.cache.get(key)) is not None:
            self.hits += 1
            return r
        var = min(self.top(f), self.top(g))               # верхня зі змінних, що зустрілися
        f0, f1 = self.cofactors(f, var)
        g0, g1 = self.cofactors(g, var)
        r = self.mk(var, self.apply(op, f0, g0), self.apply(op, f1, g1))
        self.cache[key] = r
        return r

    def size(self, u: int) -> int:
        seen: set[int] = set()
        stack = [u]
        while stack:
            x = stack.pop()
            if x < 2 or x in seen:
                continue
            seen.add(x)
            stack.extend((self.nodes[x].lo, self.nodes[x].hi))
        return len(seen)

    # Скільки з 2^nvars наборів дають 1. int — точно, без округлень.
    def count(self, u: int) -> int:
        memo: dict[int, int] = {}

        def rec(x: int) -> int:
            if x < 2:
                return x                                  # 0 → жодного набору, 1 → один
            if (r := memo.get(x)) is not None:
                return r
            var, lo, hi = self.nodes[x]
            r = (rec(lo) << (self.top(lo) - var - 1)) + (rec(hi) << (self.top(hi) - var - 1))
            memo[x] = r
            return r

        return rec(u) << self.top(u)                      # рівні НАД коренем теж пропущені

    # Набір, на якому f = 1. У зведеній діаграмі кожен вузол, крім 0, здійсненний,
    # тому спуск ніколи не заходить у глухий кут — жодного вороття.
    def witness(self, u: int) -> dict[int, int] | None:
        if u == ZERO:
            return None
        env = dict.fromkeys(range(self.nvars), 0)         # пропущені змінні байдужі — хай 0
        while u != ONE:
            var, lo, hi = self.nodes[u]
            take_high = lo == ZERO
            env[var] = int(take_high)
            u = hi if take_high else lo
        return env


# ─────────── ЧАСТИНА 2: два суматори й дослід ───────────
def build_adder(b: Bdd, n: int, drop_cin_term: bool = False) -> tuple[int, int]:
    """Змінні: a0 b0 a1 b1 ... a(n-1) b(n-1) cin. Повертає (ланцюжок, прискорений)."""
    A = [b.variable(2 * i) for i in range(n)]
    B = [b.variable(2 * i + 1) for i in range(n)]
    cin = b.variable(2 * n)

    c = cin                                               # ланцюжок: c = G_i + P_i·c
    for i in range(n):
        g = b.apply("and", A[i], B[i])
        p = b.apply("or", A[i], B[i])
        c = b.apply("or", g, b.apply("and", p, c))
    ripple = c

    G = [b.apply("and", A[i], B[i]) for i in range(n)]    # прискорений: усі переноси наперед
    P = [b.apply("xor", A[i], B[i]) for i in range(n)]
    cla = ZERO
    for i in range(n):
        t = G[i]
        for j in range(i + 1, n):
            t = b.apply("and", t, P[j])
        cla = b.apply("or", cla, t)
    if not drop_cin_term:                                 # доданок cin·P0···P(n-1)
        t = cin
        for j in range(n):
            t = b.apply("and", t, P[j])
        cla = b.apply("or", cla, t)

    return ripple, cla


def build_pairs(b: Bdd, n: int, interleaved: bool) -> int:
    """f = x0·y0 + x1·y1 + ... — щоб побачити ціну порядку змінних."""
    f = ZERO
    for i in range(n):
        x = b.variable(2 * i if interleaved else i)
        y = b.variable(2 * i + 1 if interleaved else n + i)
        f = b.apply("or", f, b.apply("and", x, y))
    return f


if __name__ == "__main__":
    print("=== той самий перенос, зібраний двома різними схемами ===")
    print("  n | вузлів | rc == cla | наборів Cout=1 | усього наборів")
    for n in (4, 16, 32):
        b = Bdd(2 * n + 1)
        rc, cla = build_adder(b, n)
        print(f" {n:2d} | {b.size(rc):6d} | {'ТАК' if rc == cla else 'НІ':>9} |"
              f" {b.count(rc):14d} | {2 ** (2 * n + 1)}")

    print("\n=== а тепер у прискореному забули доданок cin·P0···P(n-1) ===")
    n = 16
    b = Bdd(2 * n + 1)
    rc, bad = build_adder(b, n, drop_cin_term=True)
    miter = b.apply("xor", rc, bad)                       # рівно ті набори, де схеми РІЗНЯТЬСЯ
    print(f"  rc == cla: {'ТАК' if rc == bad else 'НІ'} | вузлів у різниці: {b.size(miter)}"
          f" | наборів-контрприкладів: {b.count(miter)} з {2 ** (2 * n + 1)}")
    env = b.witness(miter)
    a_val = sum(env[2 * i] << i for i in range(n))
    b_val = sum(env[2 * i + 1] << i for i in range(n))
    cin_val = env[2 * n]
    print(f"  контрприклад: a={a_val}, b={b_val}, cin={cin_val}")
    print(f"  чесна арифметика: (a+b+cin) >> {n} = {(a_val + b_val + cin_val) >> n}"
          f"   ← ланцюжок каже це, поламаний прискорений каже 0")

    print("\n=== ціна порядку змінних: f = x0·y0 + ... + x(n-1)·y(n-1) ===")
    print("  n | чергуючи | групами | у скільки разів")
    for n in range(2, 13):
        bi, bg = Bdd(2 * n), Bdd(2 * n)
        si = bi.size(build_pairs(bi, n, True))
        sg = bg.size(build_pairs(bg, n, False))
        print(f" {n:2d} | {si:8d} | {sg:7d} | {sg / si:.0f}×")

    print("\n=== кеш ===")
    for n in (8, 32):
        b = Bdd(2 * n + 1)
        build_adder(b, n)
        print(f"  суматор n={n:2d}: викликів apply={b.calls}, влучань={b.hits}"
              f" ({100 * b.hits / b.calls:.0f}%), вузлів у таблиці={len(b.nodes) - 2}")
