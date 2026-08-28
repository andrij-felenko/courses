function annuityFactor(r: number, years = 5): number {
  // A(r) = сума 1/(1+r)^t за t=1..years — згортає рівний річний потік у теперішню суму
  let a = 0;
  for (let t = 1; t <= years; t++) a += 1 / (1 + r) ** t;
  return a;
}

const pvBuild = (r: number) => 150 + 20 * annuityFactor(r); // 150 наперед + 20/рік
const pvBuy = (r: number) => 60 * annuityFactor(r);         // 60/рік підписки

for (const r of [0.10, 0.35]) {
  const b = pvBuild(r), s = pvBuy(r);
  const winner = b < s ? "збудувати" : "купити";
  console.log(`r=${(r * 100).toFixed(0)}%: build=${b.toFixed(1)} buy=${s.toFixed(1)} → ${winner}`);
}
