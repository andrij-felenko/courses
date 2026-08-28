// ── Модель даних: вершина, ребро, факт ──────────────────────────────────────

/** Вершина графа: множина «усі, хто має relation до object». */
type Userset = { object: string; relation: string };

/** Те, на що вказує ребро: або конкретна людина (листок), або інша вершина. */
type Subject = { user: string } | Userset;

type Tuple = { object: string; relation: string; subject: Subject };

const key = (u: { object: string; relation: string }) => `${u.object}#${u.relation}`;
const isUser = (s: Subject): s is { user: string } => "user" in s;

// ── Правила: ребра, яких у сховищі немає ────────────────────────────────────
type Rule =
  | { kind: "this" }                              // те, що справді лежить у сховищі
  | { kind: "computed"; relation: string }        // той самий object, інше відношення
  | { kind: "walk"; via: string; then: string };  // піти за зв'язком і спитати там

/** namespace → relation → об'єднання правил. */
type Config = Record<string, Record<string, Rule[]>>;

const config: Config = {
  group: { member: [{ kind: "this" }] },
  folder: {
    parent: [{ kind: "this" }],
    editor: [{ kind: "this" }, { kind: "walk", via: "parent", then: "editor" }],
    viewer: [{ kind: "this" }, { kind: "computed", relation: "editor" },
             { kind: "walk", via: "parent", then: "viewer" }],
  },
  doc: {
    parent: [{ kind: "this" }],
    editor: [{ kind: "this" }, { kind: "walk", via: "parent", then: "editor" }],
    viewer: [{ kind: "this" }, { kind: "computed", relation: "editor" },
             { kind: "walk", via: "parent", then: "viewer" }],
  },
};

// невідомий namespace чи relation — нуль правил, тобто відмова за замовчанням
const rulesFor = (u: Userset): Rule[] =>
  config[u.object.split(":")[0]]?.[u.relation] ?? [];

// ── Сховище: читає ПАЧКУ ключів одним походом ───────────────────────────────
interface Store {
  readMany(keys: Userset[]): Promise<Map<string, Subject[]>>;
}

class MemoryStore implements Store {
  private idx = new Map<string, Subject[]>();
  trips = 0;                                   // скільки разів ми сходили у сховище
  constructor(tuples: Tuple[]) {
    for (const t of tuples) {
      if (!this.idx.has(key(t))) this.idx.set(key(t), []);
      this.idx.get(key(t))!.push(t.subject);
    }
  }
  async readMany(keys: Userset[]): Promise<Map<string, Subject[]>> {
    this.trips++;                              // один похід — скільки б ключів не було
    const rows = new Map<string, Subject[]>();
    for (const k of keys) rows.set(key(k), this.idx.get(key(k)) ?? []);
    return rows;
  }
}

// ── Замикання за похідними відношеннями: у сховище НЕ ходить ────────────────
function closeComputed(frontier: Userset[]): Userset[] {
  const local = new Set<string>();             // правила теж бувають кільцем
  const out: Userset[] = [];
  const stack = [...frontier];
  while (stack.length) {
    const n = stack.pop()!;
    if (local.has(key(n))) continue;
    local.add(key(n));
    out.push(n);
    for (const r of rulesFor(n))
      if (r.kind === "computed") stack.push({ object: n.object, relation: r.relation });
  }
  return out;
}

export class DepthExceeded extends Error {}

// ── Сама перевірка: обхід графа рівнями ─────────────────────────────────────
export async function check(
  store: Store, user: string, start: Userset,
  { maxDepth = 16, memo = true } = {},
): Promise<{ allowed: boolean; depth: number; trips: number }> {
  const seen = new Set<string>([key(start)]);
  let frontier = [start];
  let trips = 0;

  for (let depth = 0; depth < maxDepth; depth++) {
    if (frontier.length === 0) return { allowed: false, depth, trips };  // граф вичерпано

    const nodes = closeComputed(frontier);

    // (1) зібрати ВСЕ, що доведеться прочитати на цьому рівні
    const want: Userset[] = [];
    const wanted = new Set<string>();
    const add = (u: Userset) => {
      if (wanted.has(key(u))) return;
      wanted.add(key(u));
      want.push(u);
    };
    for (const n of nodes)
      for (const r of rulesFor(n)) {
        if (r.kind === "this") add(n);
        if (r.kind === "walk") add({ object: n.object, relation: r.via });
      }

    // (2) один похід у сховище на весь рівень
    const rows = await store.readMany(want);
    trips++;

    // (3) розбір: знайшли — виходимо; ні — складаємо наступний рівень
    const next: Userset[] = [];
    const enqueue = (u: Userset) => {
      if (memo) {
        if (seen.has(key(u))) return;          // уже розкривали — вдруге не треба
        seen.add(key(u));
      }
      next.push(u);
    };
    for (const n of nodes)
      for (const r of rulesFor(n)) {
        if (r.kind === "this")
          for (const s of rows.get(key(n)) ?? []) {
            if (isUser(s)) { if (s.user === user) return { allowed: true, depth, trips }; }
            else enqueue(s);
          }
        if (r.kind === "walk") {
          const via = { object: n.object, relation: r.via };
          for (const s of rows.get(key(via)) ?? [])
            // збережене відношення у зв'язку ігноруємо — питаємо те, що каже правило
            if (!isUser(s)) enqueue({ object: s.object, relation: r.then });
        }
      }
    frontier = next;
  }
  throw new DepthExceeded(`${key(start)}: обхід не вклався в ${maxDepth} рівнів`);
}
