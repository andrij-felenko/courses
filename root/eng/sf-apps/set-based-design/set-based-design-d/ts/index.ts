interface Option {
  name: string;
  maxThroughput: number;   // повідомлень/с без болю
  opsCostWeek: number;     // людино-годин експлуатації на тиждень
  exactlyOnce: boolean;    // доставка «точно раз»
}

// Набір кандидатів — тримаємо ЖИВИМИ, поки факт не спростує
const CANDIDATES: Option[] = [
  { name: "in-process",    maxThroughput: 2_000,     opsCostWeek: 1,  exactlyOnce: false },
  { name: "managed-queue", maxThroughput: 50_000,    opsCostWeek: 3,  exactlyOnce: false },
  { name: "kafka",         maxThroughput: 1_000_000, opsCostWeek: 12, exactlyOnce: true  },
];

type Constraint = (o: Option) => boolean;  // факт = предикат: лишаємо, хто ВИТРИМАВ

const survivors = (opts: Option[], facts: Constraint[]): Option[] =>
  opts.filter((o) => facts.every((f) => f(o)));

const facts: Constraint[] = [];

facts.push((o) => o.maxThroughput >= 20_000);  // виміряний пік навантаження
// лишились: managed-queue, kafka   (in-process відпав — доведено, не вгадано)

facts.push((o) => o.opsCostWeek <= 5);         // реальний бюджет експлуатації
// лишився: managed-queue          (kafka відпав — зайві витрати не окупились)

const alive = survivors(CANDIDATES, facts);
console.assert(alive.map((o) => o.name).join() === "managed-queue");
// один живий → рішення визріло саме, без ранньої ставки й переробки
