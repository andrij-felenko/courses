import heapq
KEY = lambda w: (len(w), w)          # шортлекс-ключ: спершу довжина, тоді абетка

def union_g(A, B):                    # A ∪ B — злиття з викиданням дублів
    def gen():
        prev = object()               # свідомо не рівний жодному рядку
        for w in heapq.merge(A(), B(), key=KEY):   # два впорядкованих у один
            if w != prev:             # дублі в злитті стоять поруч
                prev = w
                yield w
    return gen

def inter_g(A, B):                    # A ∩ B — слова, що є в обох
    def gen():
        a, b = A(), B()
        x, y = next(a, None), next(b, None)
        while x is not None and y is not None:
            if x == y:
                yield x
                x, y = next(a, None), next(b, None)
            elif KEY(x) < KEY(y):     # x «менший» — підтягуємо x
                x = next(a, None)
            else:
                y = next(b, None)
    return gen
