type Nat =
  | { tag: "zero" }
  | { tag: "succ"; pred: Nat };          // розмічене об'єднання за полем tag

const zero: Nat = { tag: "zero" };
const succ = (n: Nat): Nat => ({ tag: "succ", pred: n });

function toInt(n: Nat): number {
  return n.tag === "zero" ? 0 : 1 + toInt(n.pred);
}

function fromInt(n: number): Nat {
  return n === 0 ? zero : succ(fromInt(n - 1));
}

function add(a: Nat, b: Nat): Nat {
  return b.tag === "zero" ? a : succ(add(a, b.pred));   // a + S(b) = S(a + b)
}

function mul(a: Nat, b: Nat): Nat {
  return b.tag === "zero" ? zero : add(mul(a, b.pred), a);
}
