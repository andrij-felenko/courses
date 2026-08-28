// ── 3. Планувальник ───────────────────────────────────────────────────
const buckets = new Map<number, Set<Derived<any>>>();
let top = -1;

function enqueue(n: Derived<any>): void {
  let b = buckets.get(n.height);
  if (!b) buckets.set(n.height, b = new Set());
  b.add(n);
  if (n.height > top) top = n.height;
}

/** ФАЗА 1 — позначити застарілим усе, що нижче за течією. Жодного обчислення. */
function mark(from: Node): void {
  const walk: Derived<any>[] = [...from.subs];
  while (walk.length) {
    const n = walk.pop()!;
    if (n.markedAt === epoch) continue;      // ромб не подвоює обходу
    n.markedAt = epoch;
    enqueue(n);
    for (const s of n.subs) walk.push(s);
  }
}

/** ФАЗА 2 — обчислити позначене в порядку зростання висот. */
function settleAll(): void {
  for (let h = 0; h <= top; h++) {
    const b = buckets.get(h);
    if (b) for (const n of b) settleNode(n);
  }
  buckets.clear();
  top = -1;
}

function settleNode(n: Derived<any>): void {
  if (n.markedAt !== epoch || n.settledAt === epoch) return;
  n.settledAt = epoch;                       // «мною вже займаються»

  let dirty = false;
  for (const d of n.deps) {
    if (d instanceof Derived) settleNode(d);  // вхід має влягтися першим
    if (d.changedAt === epoch) dirty = true;
  }
  if (dirty) n.recompute();                   // ЖОДЕН вхід не змінився — не рахуємо взагалі
}
