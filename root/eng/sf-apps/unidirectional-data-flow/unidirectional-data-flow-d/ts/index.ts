type State = { usd: number; eur: number; rate: number };

type Action =
  | { kind: "набрано-долари"; text: string }
  | { kind: "набрано-євро";   text: string }
  | { kind: "курс-оновлено";  rate: number };

function update(s: State, a: Action): State {
  switch (a.kind) {
    case "набрано-долари": {
      const usd = parseMoney(a.text) ?? s.usd;
      return { ...s, usd, eur: round2(usd * s.rate) };
    }
    case "набрано-євро": {
      const eur = parseMoney(a.text) ?? s.eur;
      return { ...s, eur, usd: round2(eur / s.rate) };
    }
    case "курс-оновлено":
      return { ...s, rate: a.rate, eur: round2(s.usd * a.rate) };
  }
}
