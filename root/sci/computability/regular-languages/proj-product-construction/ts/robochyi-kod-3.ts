function complement<S>(d: DFA<S>): DFA<S> {
  return { ...d, accepts: (q) => !d.accepts(q) };   // δ тотальна за побудовою
}

function witness<S>(d: DFA<S>): string | null {
  const back = new Map<string, { from: string; via: Sym } | null>([[d.key(d.start), null]]);
  const queue: S[] = [d.start];
  for (let head = 0; head < queue.length; head++) {   // обхід завширшки СТАНАМИ
    const q = queue[head];
    if (d.accepts(q)) {
      const out: Sym[] = [];
      for (let k = d.key(q), p = back.get(k); p; k = p.from, p = back.get(k)) out.push(p.via);
      return out.reverse().join("");
    }
    for (const c of [...d.alphabet].sort()) {
      const nx = d.step(q, c), nk = d.key(nx);
      if (!back.has(nk)) { back.set(nk, { from: d.key(q), via: c }); queue.push(nx); }
    }
  }
  return null;
}

// None ⟺ L(a) ⊆ L(b); інакше — найкоротший контрприклад.
const subsetWitness = <A, B>(a: DFA<A>, b: DFA<B>) => witness(product(a, complement(b), AND));
const equivWitness  = <A, B>(a: DFA<A>, b: DFA<B>) => witness(product(a, b, XOR));
