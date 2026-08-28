// ── 2. Двійники: набір версій, кожна з версійним вектором ──
type VV = Record<string, number>;
type Version = { list: string[]; vv: VV };

const at = (v: VV, n: string) => v[n] ?? 0;

function dominates(x: VV, y: VV): boolean {       // x строго новіший за y?
  const keys = new Set([...Object.keys(x), ...Object.keys(y)]);
  let ge = true, gt = false;
  for (const k of keys) {
    if (at(x, k) < at(y, k)) ge = false;
    if (at(x, k) > at(y, k)) gt = true;
  }
  return ge && gt;
}

function sibMerge(a: Version[], b: Version[]): Version[] {
  const both = [...a, ...b], live: Version[] = [], seen = new Set<string>();
  for (const v of both) {
    const k = JSON.stringify(Object.entries(v.vv).sort());
    if (seen.has(k)) continue;                          // дубль тієї самої версії
    if (both.some((w) => dominates(w.vv, v.vv))) continue;  // хтось новіший — відкинути
    seen.add(k); live.push(v);
  }
  return live;
}
