interface Violation { id: string; detail: string; }

function checkSync(markers: Marker[], journal: Debt[]): Violation[] {
  const out: Violation[] = [];
  const byId = new Map(journal.map((d) => [d.id, d]));
  const marked = new Set(markers.map((m) => m.id));

  for (const m of markers) {                         // напрям 1: маркер → запис
    const d = byId.get(m.id);
    if (!d) out.push({ id: m.id, detail: `маркер у ${m.at} без запису в журналі` });
    else if (d.state === "closed")
      out.push({ id: m.id, detail: `маркер у ${m.at} на ЗАКРИТОМУ записі — прибрати з коду` });
  }
  for (const d of journal) {                         // напрям 2: відкритий запис → маркер
    if (d.state !== "open") continue;
    if (!marked.has(d.id)) out.push({ id: d.id, detail: "відкритий запис без жодного маркера в коді" });
    if (!d.owner.trim())   out.push({ id: d.id, detail: "відкритий борг без власника" });
  }
  return out;
}

const CMP: Record<Op, (a: number, b: number) => boolean> = {
  ">": (a, b) => a > b, ">=": (a, b) => a >= b, "<": (a, b) => a < b, "<=": (a, b) => a <= b,
};

function checkOverdue(journal: Debt[], metrics: Record<string, number>): Violation[] {
  const out: Violation[] = [];
  for (const d of journal) {
    if (d.state !== "open") continue;
    for (const c of d.trigger) {
      const v = metrics[c.metric];
      if (v === undefined)                            // метрики нема у знімку → перевірити НЕ можемо
        out.push({ id: d.id, detail: `тригер зважає на метрику "${c.metric}", якої нема у знімку — перевірити нема як` });
      else if (CMP[c.op](v, c.threshold))             // тригер став правдою, а борг відкритий → прострочено
        out.push({ id: d.id, detail: `ПРОСТРОЧЕНО: ${c.metric}=${v} ${c.op} ${c.threshold} — гасити (власник: ${d.owner || "—"})` });
    }
  }
  return out;
}
