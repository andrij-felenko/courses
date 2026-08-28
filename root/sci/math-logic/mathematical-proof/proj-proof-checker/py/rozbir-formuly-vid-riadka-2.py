class Parser:
    def __init__(self, toks):
        self.toks, self.pos = toks, 0

    def peek(self):
        return self.toks[self.pos] if self.pos < len(self.toks) else None

    def eat(self, want=None):
        t = self.peek()
        if want is not None and t != want:
            raise SyntaxError('очікував %r, знайшов %r' % (want, t))
        self.pos += 1
        return t

    def parse(self):
        tree = self.imp()
        if self.pos != len(self.toks):
            raise SyntaxError('зайві лексеми з позиції %d' % self.pos)
        return tree

    def imp(self):                       # ⟹ — найслабший, ПРАВОасоціативний
        left = self.disj()
        if self.peek() == 'imp':
            self.eat('imp')
            return ('imp', left, self.imp())   # рекурсія праворуч
        return left

    def disj(self):                      # ∨ — лівоасоціативний
        node = self.conj()
        while self.peek() == 'or':
            self.eat('or')
            node = ('or', node, self.conj())
        return node

    def conj(self):                      # ∧ — тісніший за ∨
        node = self.neg()
        while self.peek() == 'and':
            self.eat('and')
            node = ('and', node, self.neg())
        return node

    def neg(self):                       # ¬ — найтісніший
        if self.peek() == 'not':
            self.eat('not')
            return ('not', self.neg())   # ¬¬p цілком законне
        return self.atom()

    def atom(self):                      # змінна або (…)
        t = self.peek()
        if t == '(':
            self.eat('(')
            node = self.imp()            # у дужках усе спочатку
            self.eat(')')
            return node
        if isinstance(t, tuple) and t[0] == 'var':
            return self.eat()
        raise SyntaxError('очікував змінну або дужку, знайшов %r' % (t,))

def parse(s):
    return Parser(tokenize(s)).parse()
