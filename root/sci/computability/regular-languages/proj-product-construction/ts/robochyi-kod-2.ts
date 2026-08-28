function endsWith(pattern: string, alphabet: Sym[]): DFA<number> {
  const m = pattern.length;
  return {
    alphabet,
    start: 0,
    step: (i, c) => {
      const cand = pattern.slice(0, i) + c;          // що тепер у хвості
      for (let k = Math.min(cand.length, m); k > 0; k--)
        if (cand.endsWith(pattern.slice(0, k))) return k;  // найдовший уцілілий
      return 0;
    },
    accepts: (i) => i === m,
    key: String,
  };
}

function contains(pattern: string, alphabet: Sym[]): DFA<number> {
  const base = endsWith(pattern, alphabet), m = pattern.length;
  return { ...base, step: (i, c) => (i === m ? m : base.step(i, c)) };  // m — пастка
}

function notStartingWith(bad: Sym, alphabet: Sym[]): DFA<"поч" | "ок" | "мертв"> {
  return {
    alphabet,
    start: "поч",
    step: (q, c) => (q === "поч" ? (c === bad ? "мертв" : "ок") : q),
    accepts: (q) => q === "ок",
    key: (q) => q,
  };
}
