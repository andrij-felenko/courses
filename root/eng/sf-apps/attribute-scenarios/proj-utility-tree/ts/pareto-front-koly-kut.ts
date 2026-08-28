// A домінує над B: A не гірший за обома осями й строго кращий хоч за однією.
// «Кращий» = більший: більша важливість І більша складність — «драйверніший».
const dominates = (a: Scenario, b: Scenario): boolean =>
  a.importance >= b.importance && a.difficulty >= b.difficulty &&
  (a.importance > b.importance || a.difficulty > b.difficulty);

// Парето-фронт: сценарії, яких не домінує жоден інший.
function paretoFront(items: Scenario[]): Scenario[] {
  return items.filter(a => !items.some(b => dominates(b, a)));
}
