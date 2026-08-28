// ── Час: ISO-день, бо лексикографічне порівняння = хронологічне ──────
type Day = string;
const daysBetween = (from: Day, to: Day): number =>
  Math.round((Date.parse(to) - Date.parse(from)) / 86_400_000);

// ── Варіант: усе, що ми про нього знаємо ─────────────────────────────
interface Option {
  readonly name: string;
  readonly maxThroughput: number;   // повідомлень/с, які тягне без болю
  readonly opsCostWeek: number;     // людино-годин експлуатації на тиждень
  readonly exactlyOnce: boolean;    // чи дає доставку «точно раз»
}

// ── Доказовість: головний запобіжник трекера ─────────────────────────
type Evidence = "виміряно" | "документ" | "здогад";
const PROVEN: readonly Evidence[] = ["виміряно", "документ"];

interface Fact {
  readonly id: string;
  readonly says: string;              // що встановлено — людською мовою
  readonly evidence: Evidence;
  readonly source: string;            // де лежить доказ
  readonly when: Day;
  readonly holds: (o: Option) => boolean;  // хто ВИЖИВАЄ під цим фактом
}

// ── Події журналу — розмічене об'єднання ─────────────────────────────
type Event =
  | { readonly kind: "considered"; readonly when: Day; readonly option: Option; readonly why: string }
  | { readonly kind: "learned"; readonly fact: Fact }
  | { readonly kind: "retracted"; readonly when: Day; readonly factId: string; readonly why: string };

const happened = (ev: Event): Day => (ev.kind === "learned" ? ev.fact.when : ev.when);

// ── Стан — ЗГОРТКА журналу, а не збережене поле ──────────────────────
interface State {
  readonly alive: readonly Option[];
  readonly killedBy: ReadonlyMap<string, readonly Fact[]>;
  readonly facts: readonly Fact[];
}

const replay = (journal: readonly Event[], upto?: Day): State => {
  const considered: Option[] = [];
  const facts: Fact[] = [];
  const dead = new Set<string>();
  for (const ev of journal) {
    // not break, а continue: журнал може лежати не строго за датами
    if (upto !== undefined && happened(ev) > upto) continue;
    switch (ev.kind) {
      case "considered": considered.push(ev.option); break;
      case "learned": facts.push(ev.fact); break;
      case "retracted": dead.add(ev.factId); break;
    }
  }
  const live = facts.filter((f) => !dead.has(f.id));
  const alive: Option[] = [];
  const killedBy = new Map<string, readonly Fact[]>();
  for (const o of considered) {
    const killers = live.filter((f) => !f.holds(o));
    if (killers.length > 0) killedBy.set(o.name, killers);  // уся сила журналу тут
    else alive.push(o);
  }
  return { alive, killedBy, facts: live };
};
