type Expression =
  | boolean
  | number
  | string
  | { var: string }                        // Звернення до змінної стану за JSON Pointer: { "var": "/cart/total" }
  | { op: "==" | "!=" | ">" | ">=" | "<" | "<=", left: Expression, right: Expression }
  | { op: "and" | "or", args: Expression[] }
  | { op: "not", arg: Expression }
  | { op: "in", item: Expression, list: Expression[] }
  | { op: "regex", value: Expression, pattern: string }
  | { op: "+" | "-" | "*" | "/", left: Expression, right: Expression }
  | { op: "ternary", condition: Expression, true_val: Expression, false_val: Expression };
