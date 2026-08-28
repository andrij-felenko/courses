// ── Ефект як дані: опис дії, а не сама дія ──
type Effect =
  | { kind: "flag";     txId: string; reason: string }
  | { kind: "freeze";   accountId: string }
  | { kind: "setBalance"; accountId: string; amount: number }
  | { kind: "notify";   userId: string; message: string }
  | { kind: "audit";    line: string };

// План — просто список описів. Це чисті дані, у них нічого не «діється».
type Plan = Effect[];
