class Folder(ExprVisitor):
    def visit_num(self, e): return e
    def visit_var(self, e): return e
    def visit_neg(self, e):
        a = e.arg.accept(self)
        return Num(-a.value) if isinstance(a, Num) else Neg(a)
    def visit_add(self, e):
        l = e.left.accept(self); r = e.right.accept(self)
        if isinstance(l, Num) and isinstance(r, Num): return Num(l.value + r.value)
        if isinstance(l, Num) and l.value == 0: return r          # 0 + x = x
        if isinstance(r, Num) and r.value == 0: return l          # x + 0 = x
        return Add(l, r)
    def visit_mul(self, e):
        l = e.left.accept(self); r = e.right.accept(self)
        if isinstance(l, Num) and isinstance(r, Num): return Num(l.value * r.value)
        if (isinstance(l, Num) and l.value == 0) or (isinstance(r, Num) and r.value == 0): return Num(0)
        if isinstance(l, Num) and l.value == 1: return r          # 1 * x = x
        if isinstance(r, Num) and r.value == 1: return l          # x * 1 = x
        return Mul(l, r)
