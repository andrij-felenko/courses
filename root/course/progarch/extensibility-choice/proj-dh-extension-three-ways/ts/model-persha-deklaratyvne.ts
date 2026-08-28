type Cond =
  | { op: "and" | "or"; l: Cond; r: Cond }
  | { op: "==" | "<";   l: Cond; r: Cond }
  | { op: "var"; name: string }        // "time.hour", "home.mode"
  | { op: "lit"; value: string | number };

class FuelOut extends Error {}

function evalCond(n: Cond, env: Record<string, unknown>, fuel: { left: number }): unknown {
  if (--fuel.left <= 0) throw new FuelOut();   // КОЖЕН вузол коштує одиницю пального
  switch (n.op) {
    case "lit": return n.value;
    case "var": return env[n.name];
    case "and": return evalCond(n.l, env, fuel) && evalCond(n.r, env, fuel);
    case "or":  return evalCond(n.l, env, fuel) || evalCond(n.r, env, fuel);
    case "==":  return evalCond(n.l, env, fuel) === evalCond(n.r, env, fuel);
    case "<":   return (evalCond(n.l, env, fuel) as number) < (evalCond(n.r, env, fuel) as number);
  }
}
