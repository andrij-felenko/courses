/** Закон 1 — рівність. Закон 2 — НЕ рівність, а лише нерухомість другого прогону. */
function checkLaws<D, R>(
  save: (o: D) => R,
  load: (r: R) => D,
  eq: (a: D, b: D) => boolean,
  rowEq: (a: R, b: R) => boolean,
  objects: readonly D[],
  rows: readonly R[],
): string {
  const e = (r: R): R => save(load(r));

  // Обов'язок: нічого не загубити.
  for (const o of objects) {
    if (!eq(load(save(o)), o))
      throw new Error(`закон 1 впав на ${JSON.stringify(o)}: об'єкт повернувся іншим`);
  }

  // Наслідок: e(r) може НЕ дорівнювати r — але e(e(r)) мусить дорівнювати e(r).
  for (const r of rows) {
    const once = e(r), twice = e(once);
    if (!rowEq(twice, once))
      throw new Error(`закон 2 впав на ${JSON.stringify(r)}: друге збереження щось змінило`);
  }
  return "обидва закони тримаються";
}

// колонка-текст placed_at ↔ Date
const save = (d: Date) => d.toISOString();
const load = (s: string) => new Date(s);

checkLaws(save, load,
  (a, b) => a.getTime() === b.getTime(),   // рівність домену
  (a, b) => a === b,                       // рівність рядків
  [new Date("2026-07-14T00:00:00Z"), new Date("2026-07-14T09:31:07.250Z")],
  ["2026-07-14", "2026-07-14T00:00:00Z", "2026-07-14T00:00:00.000Z"]);
