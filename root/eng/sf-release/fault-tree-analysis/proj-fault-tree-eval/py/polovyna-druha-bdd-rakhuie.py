class BDD:
    def __init__(self, order):
        self.rank = {v: i for i, v in enumerate(order)}   # порядок змінних
        self.nodes = {}          # id -> (var, lo, hi)
        self.unique = {}         # (var, lo, hi) -> id   ← хеш-консинг
        self.memo = {}           # (op, a, b)   -> id    ← мемо apply
        self.next_id = 2         # 0 і 1 — термінали FALSE / TRUE

    def mk(self, var, lo, hi):
        if lo == hi:                       # надлишковий вузол — гілки збіглися
            return lo
        key = (var, lo, hi)
        if key in self.unique:             # ізоморфний вузол уже є — поділитися ним
            return self.unique[key]
        nid = self.next_id; self.next_id += 1
        self.nodes[nid] = (var, lo, hi)
        self.unique[key] = nid
        return nid

    def var(self, name):                   # BDD однієї події: ціла → 0, відмовила → 1
        return self.mk(self.rank[name], 0, 1)

    def apply(self, op, a, b):             # об'єднати дві діаграми вентилем op
        if op == "and":
            if a == 0 or b == 0: return 0
            if a == 1: return b
            if b == 1: return a
        else:  # or
            if a == 1 or b == 1: return 1
            if a == 0: return b
            if b == 0: return a
        if a == b: return a
        if a > b: a, b = b, a              # комутативність → більше влучань у мемо
        if (op, a, b) in self.memo:
            return self.memo[(op, a, b)]
        va, vb = self.nodes[a][0], self.nodes[b][0]
        top = min(va, vb)                  # спільна верхня змінна
        def cof(n, v):                     # кофактори по змінній v
            if n > 1 and self.nodes[n][0] == v:
                return self.nodes[n][1], self.nodes[n][2]
            return n, n                    # v нема в n — обидва кофактори = n
        a0, a1 = cof(a, top); b0, b1 = cof(b, top)
        r = self.mk(top, self.apply(op, a0, b0), self.apply(op, a1, b1))
        self.memo[(op, a, b)] = r
        return r

    def probability(self, root, p):
        """Один прохід: P(вузол) = (1−p)·P(гілка-0) + p·P(гілка-1)."""
        memo = {0: 0.0, 1: 1.0}
        def rec(n):
            if n in memo: return memo[n]
            v, lo, hi = self.nodes[n]
            memo[n] = (1 - p[v]) * rec(lo) + p[v] * rec(hi)
            return memo[n]
        return rec(root)

def build(bdd, tree, node):                # згорнути дерево у BDD знизу вгору
    if node not in tree:
        return bdd.var(node)
    kind, inputs = tree[node]
    r = build(bdd, tree, inputs[0])
    for child in inputs[1:]:
        r = bdd.apply(kind, r, build(bdd, tree, child))
    return r

tree  = {"TOP": ("or", ["POWER", "PUMPS"]), "PUMPS": ("and", ["PUMP_A", "PUMP_B"])}
order = ["POWER", "PUMP_A", "PUMP_B"]
prob  = {"POWER": 0.001, "PUMP_A": 0.01, "PUMP_B": 0.01}

bdd  = BDD(order)
root = build(bdd, tree, "TOP")
print(bdd.probability(root, [prob[v] for v in order]))   # 0.0010999
