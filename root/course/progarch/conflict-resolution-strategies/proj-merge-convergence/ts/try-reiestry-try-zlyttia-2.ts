// ── 3. OR-Set: на елемент — теги додавань і теги знятих (тумбстоуни) ──
type ORSet = { add: Record<string, Set<string>>; rem: Record<string, Set<string>> };

function orMerge(a: ORSet, b: ORSet): ORSet {
  const out: ORSet = { add: {}, rem: {} };
  for (const s of [a, b])
    for (const kind of ["add", "rem"] as const)
      for (const [e, tags] of Object.entries(s[kind])) {
        out[kind][e] ??= new Set();
        for (const t of tags) out[kind][e].add(t);
      }
  return out;
}

// елемент живий, поки має бодай один доданий, але не знятий тег
function orValue(s: ORSet): Set<string> {
  const live = new Set<string>();
  for (const [e, tags] of Object.entries(s.add)) {
    const rem = s.rem[e] ?? new Set<string>();
    if ([...tags].some((t) => !rem.has(t))) live.add(e);
  }
  return live;
}
