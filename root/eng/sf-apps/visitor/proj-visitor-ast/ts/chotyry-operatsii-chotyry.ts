class Evaluator implements ExprVisitor<number> {
  constructor(private env: Record<string, number>) {}
  visitNum(e: Num): number { return e.value; }
  visitVar(e: Var): number {
    if (!(e.name in this.env)) throw new Error(`змінна ${e.name} не зв'язана`);
    return this.env[e.name];
  }
  visitNeg(e: Neg): number { return -e.arg.accept(this); }
  visitAdd(e: Add): number { return e.left.accept(this) + e.right.accept(this); }
  visitMul(e: Mul): number { return e.left.accept(this) * e.right.accept(this); }
}
