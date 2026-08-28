// Внесок стратегії в ОДИН атрибут: вага стейкхолдера й корисність до/після (0..100).
interface Contribution {
  attribute: string;
  weight: number;   // наскільки атрибут важливий стейкхолдерам
  before: number;   // корисність зараз
  after: number;    // корисність, якщо стратегію впровадити
}

interface Strategy {
  name: string;
  cost: number;               // вартість, тижні
  contribs: Contribution[];
}

// CBAM: вигода = Σ вага·(корисність_після − корисність_до)
function benefit(s: Strategy): number {
  return s.contribs.reduce((acc, c) => acc + c.weight * (c.after - c.before), 0);
}

function roi(s: Strategy): number {
  return s.cost ? benefit(s) / s.cost : Infinity;
}
