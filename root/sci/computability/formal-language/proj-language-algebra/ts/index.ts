// ── Подання «предикат»: мова — функція «слово → чи належить» ──────────────
type Pred = (w: string) => boolean;
const emptyP:   Pred = _ => false;             // ∅  — не містить нічого
const epsP:     Pred = w => w === "";          // {ε} — лише порожнє слово
const wordP  = (s: string): Pred => w => w === s;                 // {s}
const sigmaP = (al: string): Pred => w => [...w].every(c => al.includes(c));  // Σ*

// ── Подання «генератор»: мова — джерело свіжого лінивого потоку слів ──────
type Lang = () => Generator<string>;
const emptyG: Lang = function* () {};              // ∅  — нічого не видає
const epsG:   Lang = function* () { yield ""; };   // {ε} — рівно одне слово: ε
const wordG = (s: string): Lang => function* () { yield s; };     // {s}
function* sigmaG(al: string): Generator<string> {                 // Σ* шортлекс
  for (let n = 0; ; n++)
    for (let i = 0; i < al.length ** n; i++) {     // слова довжини n — числа 0…kⁿ−1
      let w = "", r = i;
      for (let p = 0; p < n; p++) { w = al[r % al.length] + w; r = (r / al.length) | 0; }
      yield w;
    }
}
