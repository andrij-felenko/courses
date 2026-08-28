// Вузли дерева — кожен уміє тільки прийняти відвідувача й покликати свій visit.
interface Expr {
  accept<R>(v: Visitor<R>): R;
}

class Num implements Expr {
  constructor(readonly value: number) {}
  accept<R>(v: Visitor<R>): R { return v.visitNum(this); }
}
class Add implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  accept<R>(v: Visitor<R>): R { return v.visitAdd(this); }
}
class Mul implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  accept<R>(v: Visitor<R>): R { return v.visitMul(this); }
}

// Операція — окремий об'єкт. Один метод на кожен вид вузла.
interface Visitor<R> {
  visitNum(n: Num): R;
  visitAdd(a: Add): R;
  visitMul(m: Mul): R;
}

// Прохід 1: обчислити значення (R = number).
class Eval implements Visitor<number> {
  visitNum(n: Num): number { return n.value; }
  visitAdd(a: Add): number { return a.left.accept(this) + a.right.accept(this); }
  visitMul(m: Mul): number { return m.left.accept(this) * m.right.accept(this); }
}

// Прохід 2: надрукувати у дужках (R = string).
class Print implements Visitor<string> {
  visitNum(n: Num): string { return String(n.value); }
  visitAdd(a: Add): string { return `(${a.left.accept(this)} + ${a.right.accept(this)})`; }
  visitMul(m: Mul): string { return `(${m.left.accept(this)} * ${m.right.accept(this)})`; }
}
