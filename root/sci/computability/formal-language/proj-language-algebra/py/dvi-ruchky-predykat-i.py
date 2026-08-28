from itertools import count, product

# ── Подання «предикат»: мова — функція «слово → чи належить» ──────────────
empty_p = lambda w: False            # ∅  — не містить нічого
eps_p   = lambda w: w == ""          # {ε} — містить лише порожнє слово
def word_p(s):   return lambda w: w == s              # {s}
def sigma_p(al): return lambda w: all(c in al for c in w)   # Σ*

# ── Подання «генератор»: мова — джерело свіжого лінивого потоку слів ──────
empty_g = lambda: iter(())           # ∅  — порожній потік, жодного слова
eps_g   = lambda: iter([""])         # {ε} — потік рівно з одного слова: ε
def word_g(s):   return lambda: iter([s])             # {s}
def sigma_g(al):                                      # Σ* у шортлекс-порядку
    def gen():
        for n in count(0):                            # довжина 0, 1, 2, …
            for t in product(al, repeat=n):
                yield "".join(t)                      # n = 0 дає рівно одне: ε
    return gen
