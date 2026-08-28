// rules.ts — самі правила, жодного доступу назовні
export type Order = { amount: number; kind: "sale" | "refund" };

const round2 = (v: number) => Math.round(v * 100) / 100;

export function netAmount(orders: Order[]): number {
  let net = 0;
  for (const o of orders) net += o.kind === "refund" ? -o.amount : o.amount;
  return Math.max(0, round2(net));
}

export function discounted(net: number): number {
  return net > 5000 ? round2(net * 0.95) : net;
}

export function totalDue(orders: Order[]): number {
  return round2(discounted(netAmount(orders)) * 1.2);   // ПДВ 20 %
}
