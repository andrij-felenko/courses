class AreaVisitor(ShapeVisitor):        # операція «площа» — ЦІЛА, в одному класі
    def visit_circle(self, c):    return pi * c.r * c.r
    def visit_rectangle(self, r): return r.w * r.h
    def visit_triangle(self, t):  return t.base * t.height / 2

class SvgVisitor(ShapeVisitor):         # інша операція — інший клас
    def visit_circle(self, c):    return f'<circle r="{c.r}"/>'
    def visit_rectangle(self, r): return f'<rect width="{r.w}" height="{r.h}"/>'
    def visit_triangle(self, t):  return f'<polygon points="0,0 {t.base},0 0,{t.height}"/>'

shapes = [Circle(2), Rectangle(3, 4), Triangle(6, 2)]

total  = sum(s.accept(AreaVisitor()) for s in shapes)       # 12.566… + 12 + 6 = 30.566…
markup = "\n".join(s.accept(SvgVisitor()) for s in shapes)
