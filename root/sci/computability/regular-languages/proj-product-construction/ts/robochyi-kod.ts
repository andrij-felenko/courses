type Sym = string;

interface DFA<S> {
  alphabet: Sym[];
  start: S;
  step: (q: S, c: Sym) => S;   // тотальна за побудовою: функція, а не таблиця
  accepts: (q: S) => boolean;
  key: (q: S) => string;       // канонічний ключ: Map порівнює обʼєкти за ПОСИЛАННЯМ
}

const AND  = (x: boolean, y: boolean) => x && y;    // L₁ ∩ L₂
const OR   = (x: boolean, y: boolean) => x || y;    // L₁ ∪ L₂
const DIFF = (x: boolean, y: boolean) => x && !y;   // L₁ ∖ L₂
const XOR  = (x: boolean, y: boolean) => x !== y;   // L₁ ⊕ L₂

// Добуток — просто запис із п'яти полів: жодного стану не збудовано наперед.
function product<A, B>(a: DFA<A>, b: DFA<B>,
                       op: (x: boolean, y: boolean) => boolean): DFA<[A, B]> {
  return {
    alphabet: a.alphabet,
    start: [a.start, b.start],
    step: ([p, q], c) => [a.step(p, c), b.step(q, c)],
    accepts: ([p, q]) => op(a.accepts(p), b.accepts(q)),
    key: ([p, q]) => `${a.key(p)}|${b.key(q)}`,
  };
}

function run<S>(d: DFA<S>, word: string): boolean {
  let q = d.start;
  for (const c of word) {
    if (!d.alphabet.includes(c)) throw new Error(`символ '${c}' поза алфавітом`);
    q = d.step(q, c);
  }
  return d.accepts(q);
}

// Матеріалізувати досяжні стани — лише коли вони справді потрібні.
function explore<S>(d: DFA<S>): S[] {
  const seen = new Set([d.key(d.start)]);
  const out: S[] = [d.start];
  for (let head = 0; head < out.length; head++)
    for (const c of d.alphabet) {
      const nx = d.step(out[head], c), nk = d.key(nx);
      if (!seen.has(nk)) { seen.add(nk); out.push(nx); }
    }
  return out;
}
