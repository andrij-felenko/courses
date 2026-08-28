const shuffle = <T,>(xs: T[]) =>
  xs.map((x) => [Math.random(), x] as const).sort((p, q) => p[0] - q[0]).map((p) => p[1]);

// канонічний «відбиток» стану — щоб порівнювати репліки попри порядок усередині структур
const lwwKey = (s: LWW | null) => s ? JSON.stringify([[...s.val].sort(), s.ts, s.node]) : "∅";
const sibKey = (s: Version[]) =>
  JSON.stringify(s.map((v) => [[...v.list].sort(), Object.entries(v.vv).sort()]).sort());
const dump = (m: Record<string, Set<string>>) =>
  Object.entries(m).map(([e, t]) => [e, [...t].sort()]).sort();
const orKey = (s: ORSet) => JSON.stringify([dump(s.add), dump(s.rem)]);

function converge<S, F>(
  merge: (s: S, f: F) => S, empty: S, frags: F[],
  key: (s: S) => string, replicas = 1000,
): number {
  const seen = new Set<string>();
  for (let r = 0; r < replicas; r++) {
    const repeats = shuffle(frags).slice(0, Math.floor(Math.random() * (frags.length + 1)));
    const order = shuffle([...frags, ...repeats]);   // випадковий порядок + повтори
    let st = empty;
    for (const f of order) st = merge(st, f);
    seen.add(key(st));
  }
  return seen.size;                                   // 1 ⟺ усі репліки зійшлися
}

console.assert(converge(lwwMerge, null, lwwFrags, lwwKey) === 1, "LWW не зійшовся");
console.assert(converge(sibMerge, [],   sibFrags, sibKey) === 1, "двійники не зійшлися");
console.assert(converge(orMerge, { add: {}, rem: {} }, orFrags, orKey) === 1, "OR-Set не зійшовся");
