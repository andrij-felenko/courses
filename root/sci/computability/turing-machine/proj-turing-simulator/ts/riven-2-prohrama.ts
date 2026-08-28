const encode = (d: Delta): string =>
  [...d].sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([k, r]) => { const [q, c] = k.split(","); return q + c + r.write + r.move + r.next; })
    .join("");

const load = (d: Delta, w: string, start = "q0") => `^${encode(d)}#${start}|*${w}`;

function universal(tapeStr: string, limit = 200_000) {
  const T = new Map<number, string>([...tapeStr].map((c, i) => [i, c]));
  const at = (i: number) => T.get(i) ?? BL;
  let left = 0, h = 1;
  while (at(h) !== "#") h++;                       // h — межа «#», за нею стан M
  let bar = h + 3;                                 // bar — межа «|», за нею стрічка M
  for (let steps = 0; steps <= limit; steps++) {
    const q = at(h + 1) + at(h + 2);               // хто я: стан M — 2 клітинки
    if (q === "qa") return { v: "ПРИЙНЯТО" as Verdict, steps, tape: work(T, bar) };
    if (q === "qr") return { v: "ВІДКИНУТО" as Verdict, steps, tape: work(T, bar) };
    let s = bar;
    while (at(s) !== "*") s++;                     // що бачу: дійти до позначки голівки
    const c = at(s + 1);
    let p = left + 1;                              // шукаємо правило: крок сімками
    while (p < h && !(at(p) + at(p + 1) === q && at(p + 2) === c)) p += 7;
    if (p >= h) return { v: "ВІДКИНУТО" as Verdict, steps, tape: work(T, bar) };
    T.set(s + 1, at(p + 3));                       // пише
    T.set(h + 1, at(p + 5)); T.set(h + 2, at(p + 6));   // новий стан
    if (at(p + 4) === "R") {
      T.set(s, at(s + 1)); T.set(s + 1, "*");      // позначка міняється з сусідом
    } else {
      if (s - 1 === bar) {                         // ліворуч межа: посунути весь опис
        for (let i = left; i <= bar; i++) T.set(i - 1, at(i));
        T.set(bar, BL);
        left--; h--; bar--;
      }
      T.set(s, at(s - 1)); T.set(s - 1, "*");
    }
  }
  return { v: "НЕ ЗНАЮ" as Verdict, steps: limit, tape: work(T, bar) };
}

const work = (T: Map<number, string>, bar: number) =>
  [...T.keys()].filter((i) => i > bar).sort((a, b) => a - b)
    .map((i) => T.get(i)!).filter((c) => c !== "*").join("").replace(/^␣+|␣+$/g, "");
