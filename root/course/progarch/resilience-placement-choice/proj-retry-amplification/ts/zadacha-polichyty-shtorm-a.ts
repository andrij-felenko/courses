type Layer = { name: string; tries: number }; // tries: скільки спроб робить шар (1 = без повтору)

// СТЕЛЯ: кожен шар множить на свою кількість спроб. Найгірший випадок —
// кожна спроба провалюється, кожен шар вичерпує всі повтори.
const worstCase = (layers: Layer[]): number =>
  layers.reduce((acc, l) => acc * l.tries, 1);

// ОЧІКУВАНИЙ фан-аут за ймовірності збою p на спробу: шар, що робить t спроб,
// шле в середньому 1 + p + p² + … + p^(t−1) запитів (повторює лише ПІСЛЯ збою).
const expectedPerLayer = (tries: number, p: number): number => {
  let sum = 0, term = 1;
  for (let i = 0; i < tries; i++) { sum += term; term *= p; }
  return sum; // = (1 − p^tries) / (1 − p) при p < 1
};
const expectedFanout = (layers: Layer[], p: number): number =>
  layers.reduce((acc, l) => acc * expectedPerLayer(l.tries, p), 1);

// Шлях команди DH: три шари повторюють по 3 спроби, далі — залежність.
const path: Layer[] = [
  { name: "застосунок", tries: 3 },
  { name: "шлюз",       tries: 3 },
  { name: "сайдкар",    tries: 3 },
];
const RPS = 500; // клік/с на ранковому піку

for (const p of [0.0, 0.3, 0.7, 1.0]) {
  const f = expectedFanout(path, p);
  console.log(`p=${p}: фан-аут ${f.toFixed(2)}× → ${Math.round(f * RPS)} req/s`);
}
console.log(`стеля: ${worstCase(path)}× → ${worstCase(path) * RPS} req/s`);
