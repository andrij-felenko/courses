interface Tradeoff {
  param: string;
  up:   { attr: Attribute; who: string };
  down: { attr: Attribute; who: string };
}

function tradeoffPoints(reg: Stakeholder[], params: Parameter[]): Tradeoff[] {
  // Один прохід: групуємо ЛИШЕ високовагомих за їхньою турботою.
  const byConcern = new Map<Attribute, Stakeholder[]>();
  for (const s of reg) {
    if (salienceScore(s) < HIGH_SALIENCE) continue;
    const list = byConcern.get(s.concern) ?? [];
    list.push(s);
    byConcern.set(s.concern, list);
  }

  const out: Tradeoff[] = [];
  for (const p of params) {
    const up   = p.pushes.filter(x => x.dir > 0);  // хто виграє від параметра
    const down = p.pushes.filter(x => x.dir < 0);  // хто програє
    for (const u of up) for (const d of down) {     // лише ПРОТИЛЕЖНІ знаки — це й є компроміс
      for (const su of byConcern.get(u.attr) ?? [])
        for (const sd of byConcern.get(d.attr) ?? []) {
          if (su.name === sd.name) continue;        // не зіштовхуй людину з нею ж
          out.push({ param: p.name,
                     up:   { attr: u.attr, who: su.name },
                     down: { attr: d.attr, who: sd.name } });
        }
    }
  }
  return out;
}
