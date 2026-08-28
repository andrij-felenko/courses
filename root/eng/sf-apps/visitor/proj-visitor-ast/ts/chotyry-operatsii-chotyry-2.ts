type Printed = { text: string; prec: number };

class Printer implements ExprVisitor<Printed> {
  visitNum(e: Num): Printed { return { text: String(e.value), prec: 4 }; }
  visitVar(e: Var): Printed { return { text: e.name, prec: 4 }; }
  visitNeg(e: Neg): Printed {
    const a = e.arg.accept(this);
    return { text: "-" + this.wrap(a, 4), prec: 3 };     // -(x + 3), але -5 без дужок
  }
  visitMul(e: Mul): Printed {
    const l = e.left.accept(this), r = e.right.accept(this);
    return { text: this.wrap(l, 2) + " * " + this.wrap(r, 2), prec: 2 };
  }
  visitAdd(e: Add): Printed {
    const l = e.left.accept(this), r = e.right.accept(this);
    return { text: this.wrap(l, 1) + " + " + this.wrap(r, 1), prec: 1 };
  }
  private wrap(p: Printed, need: number): string {    // дужки, лише якщо дитина слабша
    return p.prec < need ? "(" + p.text + ")" : p.text;
  }
}
