interface Ranked extends Scenario {
  attribute: string;
  score: number;      // важливість × складність
}

// Ключова ухвала — ДОБУТОК, не сума.
const score = (s: Scenario): number => s.importance * s.difficulty;

function rank(tree: UtilityTree): Ranked[] {
  const flat: Ranked[] = [];
  for (const attr of tree.attributes)
    for (const s of attr.scenarios)
      flat.push({ ...s, attribute: attr.name, score: score(s) });

  // Спад за добутком; за рівних — важливіший наперед, тоді складніший.
  // Три ключі поспіль роблять порядок цілком детермінованим.
  flat.sort((a, b) =>
    b.score - a.score ||
    b.importance - a.importance ||
    b.difficulty - a.difficulty);
  return flat;
}

// Драйвери — крайній квадрант (В, В): і найцінніше, і найважче.
const drivers = (ranked: Ranked[]): Ranked[] =>
  ranked.filter(s => s.importance === 3 && s.difficulty === 3);
