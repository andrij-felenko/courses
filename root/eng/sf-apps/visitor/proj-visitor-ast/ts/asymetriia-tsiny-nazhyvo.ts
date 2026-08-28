type Instr =
  | { op: "push"; value: number } | { op: "load"; name: string }
  | { op: "add" } | { op: "mul" } | { op: "neg" };

class Compiler implements ExprVisitor<Instr[]> {
  visitNum(e: Num): Instr[]  { return [{ op: "push", value: e.value }]; }
  visitVar(e: Var): Instr[]  { return [{ op: "load", name: e.name }]; }
  visitNeg(e: Neg): Instr[]  { return [...e.arg.accept(this), { op: "neg" }]; }
  visitAdd(e: Add): Instr[]  { return [...e.left.accept(this), ...e.right.accept(this), { op: "add" }]; }
  visitMul(e: Mul): Instr[]  { return [...e.left.accept(this), ...e.right.accept(this), { op: "mul" }]; }
}

e.accept(new Compiler());
// [push 2, load x, push 3, add, mul, load x, neg, add]
