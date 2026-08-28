interface Expr {
  eval(): number;
  print(): string;   // щоб додати друк, довелося ВІДКРИТИ інтерфейс…
}

class Num implements Expr {
  constructor(readonly value: number) {}
  eval(): number { return this.value; }
  print(): string { return String(this.value); }        // …і КОЖЕН клас
}
class Add implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  eval(): number { return this.left.eval() + this.right.eval(); }
  print(): string { return `(${this.left.print()} + ${this.right.print()})`; }
}
class Mul implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  eval(): number { return this.left.eval() * this.right.eval(); }
  print(): string { return `(${this.left.print()} * ${this.right.print()})`; }
}
