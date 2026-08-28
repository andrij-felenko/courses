class Printer(ExprVisitor):
    def visit_num(self, e): return (str(e.value), 4)
    def visit_var(self, e): return (e.name, 4)
    def visit_neg(self, e):
        t, p = e.arg.accept(self)
        return ("-" + self._wrap(t, p, 4), 3)           # -(x + 3), але -5 без дужок
    def visit_mul(self, e):
        lt, lp = e.left.accept(self); rt, rp = e.right.accept(self)
        return (self._wrap(lt, lp, 2) + " * " + self._wrap(rt, rp, 2), 2)
    def visit_add(self, e):
        lt, lp = e.left.accept(self); rt, rp = e.right.accept(self)
        return (self._wrap(lt, lp, 1) + " + " + self._wrap(rt, rp, 1), 1)
    @staticmethod
    def _wrap(text, prec, need):                        # дужки, лише якщо дитина слабша
        return f"({text})" if prec < need else text
