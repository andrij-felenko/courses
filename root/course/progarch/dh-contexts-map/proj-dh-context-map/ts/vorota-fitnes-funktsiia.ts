// ownerOf(шлях) -> контекст за найдовшим коренем і сам сканер import-ів —
// ті самі, що в загальній перевірці; тут лише DH-вирок поверх знайдених ребер.
function verdict(from: string, to: string, target: string): string | null {
  if (from === to) return null;                 // всередині контексту — вільно
  const dst = MAP[to];
  if (!dst) return null;                         // зовнішній пакет — окрема перевірка (див. пастки)
  const pairOk = dst.open || to in MAP[from].allow;
  if (!pairOk) return `неоголошене ребро ${from} → ${to}`;
  if (!target.startsWith(dst.pub))
    return `${from} тягне НУТРОЩІ ${to}: ${target} (дозволено лише ${dst.pub})`;
  return null;
}

type Imp = { fromFile: string; target: string };   // джерело ребра — сканер import-ів

function audit(imports: Imp[], ownerOf: (p: string) => string | null): string[] {
  const bad: string[] = [];
  for (const { fromFile, target } of imports) {
    const from = ownerOf(fromFile), to = ownerOf(target);
    if (from === null || to === null) continue;      // поза мапою — не наша межа
    const v = verdict(from, to, target);
    if (v) bad.push(v);
    // структурні контракти поверх пер-ребра:
    if (MAP[to]?.isolated && from !== to) bad.push(`окремі шляхи порушено: ${from} → ${to}`);
    if ((from === "events" || from === "ids") && to !== from)
      bad.push(`${from} має бути листком, а тягне ${to}`);
  }
  return bad;
}

export function main(imports: Imp[], ownerOf: (p: string) => string | null): number {
  const bad = audit(imports, ownerOf);
  if (bad.length === 0) { console.log("мапа DH тримається"); return 0; }
  console.error("АРХІТЕКТУРНІ ПОРУШЕННЯ DH:");
  for (const b of bad) console.error("  " + b);
  return 1;                                          // exit 1 → крок CI червоний → merge заблоковано
}
