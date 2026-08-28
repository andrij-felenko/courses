interface Visitor<R> { num(n: number): R; add(l: Expr, r: Expr): R; }
interface Expr { accept<R>(v: Visitor<R>): R; }

class Num implements Expr {
  constructor(public n: number) {}
  accept<R>(v: Visitor<R>): R { return v.num(this.n); }   // подвійна диспетчеризація
}
class Add implements Expr {
  constructor(public l: Expr, public r: Expr) {}
  accept<R>(v: Visitor<R>): R { return v.add(this.l, this.r); }
}

// нова ОПЕРАЦІЯ = новий відвідувач; жоден вузол не чіпаємо:
class Eval implements Visitor<number> {
  num(n) { return n; }
  add(l, r) { return l.accept(this) + r.accept(this); }
}
