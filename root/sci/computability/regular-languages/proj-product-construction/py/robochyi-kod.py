from collections import deque

class DFA:
    """Повний детермінований автомат: із КОЖНОГО стану по КОЖНОМУ символу
    веде рівно один перехід."""
    def __init__(self, alphabet, states, delta, start, accepting):
        self.alphabet = alphabet      # множина символів
        self.states = states          # множина станів (будь-що хешоване)
        self.delta = delta            # (стан, символ) -> стан
        self.start = start
        self.accepting = accepting    # підмножина states
        for q in states:              # тотальність — умова коректності доповнення
            for c in alphabet:
                assert (q, c) in delta, "немає переходу з %r по %r" % (q, c)

    def accepts(self, word):
        q = self.start
        for c in word:
            if c not in self.alphabet:
                raise ValueError("символ %r поза алфавітом" % c)
            q = self.delta[(q, c)]
        return q in self.accepting


AND  = lambda x, y: x and y        # L₁ ∩ L₂
OR   = lambda x, y: x or y         # L₁ ∪ L₂
DIFF = lambda x, y: x and not y    # L₁ ∖ L₂
XOR  = lambda x, y: x != y         # L₁ ⊕ L₂

def product(a, b, accept):
    """Добутковий автомат. accept вирішує, ЯКА булева операція вийде.
    Будуємо ЛІНИВО: обхід завширшки від стартової пари — недосяжні пари
    навіть не створюються."""
    assert a.alphabet == b.alphabet, "спільний алфавіт обов'язковий"
    start = (a.start, b.start)
    states, delta, accepting = {start}, {}, set()
    queue = deque([start])
    while queue:
        p, q = queue.popleft()
        if accept(p in a.accepting, q in b.accepting):
            accepting.add((p, q))
        for c in a.alphabet:
            nxt = (a.delta[(p, c)], b.delta[(q, c)])
            delta[((p, q), c)] = nxt
            if nxt not in states:
                states.add(nxt)
                queue.append(nxt)
    return DFA(a.alphabet, states, delta, start, accepting)
