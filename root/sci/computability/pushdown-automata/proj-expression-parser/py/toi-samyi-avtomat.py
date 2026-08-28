class Parser:
    """Кожне правило граматики — окрема функція. Явного стека тут немає."""

    def __init__(self, src):
        self.toks = tokenize(src)        # той самий лексер
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def eat(self, want=None):
        t = self.peek()
        if want is not None and t != want:
            raise SyntaxError("очікували «%s», а тут %r" % (want, t))
        self.i += 1
        return t

    def expr(self):                      # expr → term (('+' | '−') term)*
        v = self.term()
        while self.peek() in ('+', '-'):
            v = v + self.term() if self.eat() == '+' else v - self.term()
        return v

    def term(self):                      # term → power (('*' | '/') power)*
        v = self.power()
        while self.peek() in ('*', '/'):
            v = v * self.power() if self.eat() == '*' else v / self.power()
        return v

    def power(self):                     # power → factor ('^' power)?
        v = self.factor()
        if self.peek() == '^':
            self.eat()
            return v ** self.power()     # рекурсія ПРАВОРУЧ → правоасоціативність
        return v

    def factor(self):                    # factor → число | '(' expr ')' | '−' factor
        t = self.peek()
        if isinstance(t, float):
            return self.eat()
        if t == '-':                     # унарний мінус: тут він ні з чим не плутається
            self.eat()
            return -self.factor()
        if t == '(':
            self.eat()
            v = self.expr()              # ← вертаємося на самий верх: нова зона пріоритету
            self.eat(')')                # дужка мусить закритися
            return v
        raise SyntaxError("очікували число або «(», а тут %r" % (t,))

def evaluate(src):
    p = Parser(src)
    v = p.expr()
    if p.peek() is not None:             # дійшли до кінця? інакше десь зайве
        raise SyntaxError("зайве після виразу: %r" % (p.peek(),))
    return v
