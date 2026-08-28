class Folder implements ExprVisitor<Expr> {
  visitNum(e: Num): Expr { return e; }
  visitVar(e: Var): Expr { return e; }
  visitNeg(e: Neg): Expr {
    const a = e.arg.accept(this);
    return a instanceof Num ? new Num(-a.value) : new Neg(a);
  }
  visitAdd(e: Add): Expr {
    const l = e.left.accept(this), r = e.right.accept(this);
    if (l instanceof Num && r instanceof Num) return new Num(l.value + r.value);
    if (l instanceof Num && l.value === 0) return r;      // 0 + x = x
    if (r instanceof Num && r.value === 0) return l;      // x + 0 = x
    return new Add(l, r);
  }
  visitMul(e: Mul): Expr {
    const l = e.left.accept(this), r = e.right.accept(this);
    if (l instanceof Num && r instanceof Num) return new Num(l.value * r.value);
    if ((l instanceof Num && l.value === 0) || (r instanceof Num && r.value === 0)) return new Num(0);
    if (l instanceof Num && l.value === 1) return r;      // 1 * x = x
    if (r instanceof Num && r.value === 1) return l;      // x * 1 = x
    return new Mul(l, r);
  }
}
