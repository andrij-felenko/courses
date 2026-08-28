interface Deferral {
  carryPerWeek: number;   // c — накладні за тиждень тримання відкритим
  weeksToLRM: number;     // t* — коли настане відповідальний момент
  reversalCost: number;   // C_r — ціна відкоту хибного вибору
  wrongNow: number;       // p(0) — ймовірність хибитися, обравши зараз
  wrongAtLRM: number;     // p(t*) — ймовірність хибитися на моменті
}

// Скільки коштує чесно дочекатися відповідального моменту.
const costOfDeferring = (d: Deferral): number =>
  d.carryPerWeek * d.weeksToLRM + d.wrongAtLRM * d.reversalCost;

// Скільки коштує вкласти R у шов (адаптер/інтерфейс) і обрати вже зараз.
const costOfSeamNow = (d: Deferral, seam: number, reduced: number): number =>
  seam + d.wrongNow * reduced;

function verdict(d: Deferral, seam: number, reduced: number): string {
  const defer = costOfDeferring(d);
  const now = costOfSeamNow(d, seam, reduced);
  return now < defer
    ? `Зроби оборотним і обирай зараз (${now.toFixed(0)} < ${defer.toFixed(0)})`
    : `Відкладай до моменту (${defer.toFixed(0)} < ${now.toFixed(0)})`;
}
