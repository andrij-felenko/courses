class Evaluator(ExprVisitor):
    def __init__(self, env): self.env = env
    def visit_num(self, e): return e.value
    def visit_var(self, e):
        if e.name not in self.env:
            raise KeyError(f"змінна {e.name} не зв'язана")
        return self.env[e.name]
    def visit_neg(self, e): return -e.arg.accept(self)
    def visit_add(self, e): return e.left.accept(self) + e.right.accept(self)
    def visit_mul(self, e): return e.left.accept(self) * e.right.accept(self)
