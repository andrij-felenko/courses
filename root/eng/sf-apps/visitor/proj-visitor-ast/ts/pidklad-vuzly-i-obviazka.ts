interface Expr {
  accept<R>(v: ExprVisitor<R>): R;          // уся обв'язка — цей один рядок
}

interface ExprVisitor<R> {                  // по методу на КОЖЕН вид вузла
  visitNum(e: Num): R;
  visitVar(e: Var): R;
  visitNeg(e: Neg): R;
  visitAdd(e: Add): R;
  visitMul(e: Mul): R;
}

class Num implements Expr {
  constructor(readonly value: number) {}
  accept<R>(v: ExprVisitor<R>): R { return v.visitNum(this); }   // я — число
}
class Var implements Expr {
  constructor(readonly name: string) {}
  accept<R>(v: ExprVisitor<R>): R { return v.visitVar(this); }
}
class Neg implements Expr {
  constructor(readonly arg: Expr) {}
  accept<R>(v: ExprVisitor<R>): R { return v.visitNeg(this); }
}
class Add implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  accept<R>(v: ExprVisitor<R>): R { return v.visitAdd(this); }
}
class Mul implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  accept<R>(v: ExprVisitor<R>): R { return v.visitMul(this); }
}
